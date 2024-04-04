import asyncio
import concurrent
import functools
import inspect
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from threading import Thread
from typing import Generic, TypeVar
from .config import default_limiter, RateLimiter
# from .config import getconfig
import logging


# logging.basicConfig(level=logging.INFO,format='%(filename)s - (asctime)s - %(lineno)d  %(levelname)s - %(message)s')

def FunctionCallWrapper(x):
    f, args, kwargs = x
    CooroutineTask = f(*args, **kwargs)
    return CooroutineTask

class disable_proxy_result(object):
    def __init__(self, normal_result):
        self.normal_result = normal_result

    def result(self):
        return self.normal_result



class normal_result(object):
    def __init__(self, normal_result, *args, **kwargs):
        self.normal_result = normal_result
        self.args = args
        self.kwargs = kwargs
    def result(self):
        return self.normal_result.result(*self.args, **self.kwargs)

class Async_Meta(type):
    def _init_loop(cls):
        cls._loop = asyncio.new_event_loop()
        cls._thread = Thread(target=cls._thread_target, args=(cls._loop,), daemon=True)
        cls._thread.start()
        cls._loop_id = uuid.uuid4()

    @property
    def loop(cls):
        if getattr(cls, '_loop', None) is None:
            Async_Meta._init_loop(cls)
        return cls._loop

    @property
    def loopid(cls):
        if getattr(cls, '_loop_id', None) is None:
            Async_Meta._init_loop(cls)
        return cls._loop_id

    @property
    def thread(cls):
        if getattr(cls, '_thread', None) is None:
            Async_Meta._init_loop(cls)
        return cls._thread

    @property
    def process_executor(cls):
        if getattr(cls, '_process_executor', None) is None:
            cls._process_executor = concurrent.futures.ProcessPoolExecutor()
        return cls._process_executor


class AsyncFuse(object, metaclass=Async_Meta):
    # thread_executor = concurrent.futures.ThreadPoolExecutor
    # process_executor = concurrent.futures.ThreadPoolExecutor
    unsync_functions = {}

    def __str__(self) -> str:
        attributes = vars(self)
        obj_dict = {key: getattr(self, key) for key in attributes}
        return str(obj_dict)
    @staticmethod
    def _thread_target(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def __init__(self, *args, **kwargs):
        self.args = []
        self.kwargs = {}

        self.cpu_bound = False
        self.io_bound = False
        self.cooroutine = False

        self.disable = False
        self.custom_proxy_handler = None
        self.time_interval = 0
        self.max_request = 0
        self.rate_limiter = RateLimiter
        self.disable_proxy_result = disable_proxy_result

        if len(args) == 1 and _isfunction(args[0]):
            self._set_func(args[0])
        else:
            self.fuseargs = args
            if 'cpu_bound' in kwargs.keys():
                self.cpu_bound = kwargs.pop('cpu_bound', False)
            if 'io_bound' in kwargs.keys():
                self.io_bound = kwargs.pop('io_bound', False)
            if 'cooroutine' in kwargs.keys():
                self.cooroutine = kwargs.pop('cooroutine', False)
            if 'disable' in kwargs.keys():
                self.disable = kwargs.pop('disable', False)
            if 'custom_proxy_handler' in kwargs.keys():
                self.custom_proxy_handler = kwargs.pop('custom_proxy_handler')
            if 'max_request' in kwargs.keys():
                self.max_request = kwargs.pop('max_request')
            if 'time_interval' in kwargs.keys():
                self.time_interval = kwargs.pop('time_interval')
            if 'rate_limiter' in kwargs.keys():
                self.rate_limiter = kwargs.pop('rate_limiter')
            self.fusekwargs = kwargs
            self.func = None

        self.process_executor = Pool(*self.fuseargs,**self.fusekwargs)
        self.thread_executor = ThreadPool(*self.fuseargs,**self.fusekwargs)
        self.rate_limiter = self.rate_limiter(max_requests=self.max_request, per_seconds=self.time_interval)


    def _set_func(self, func):
        assert _isfunction(func)
        self.func = func
        functools.update_wrapper(self, func)
        # On Windows/Mac MP turns the main module into __mp_main__ in multiprocess targets
        module = "__main__" if func.__module__ == "__mp_main__" else func.__module__
        AsyncFuse.unsync_functions[(module, func.__name__)] = func

    def __call__(self, *args, **kwargs):

        # print("event loop id : ", id(AsyncFuse.loop))

        if self.func is None:
        # if self.func:
            self._set_func(args[0])
            return self

        if self.disable:
            if inspect.iscoroutinefunction(self.func):
                new_event_loop = asyncio.new_event_loop()
                result = new_event_loop.run_until_complete( FunctionCallWrapper((self.func, args, kwargs)) )
                new_event_loop.close()
                if not self.custom_proxy_handler:
                    # return disable_proxy_result(result)
                    return AsyncFuture(future=result, custom_proxy=self.disable_proxy_result,disable=True)
                else:
                    # return self.custom_proxy_handler(result)
                    return AsyncFuture(future=result, custom_proxy=self.custom_proxy_handler, disable=True)
            else:
                if not self.custom_proxy_handler:
                    # return disable_proxy_result()
                    return AsyncFuture(future=FunctionCallWrapper((self.func, args, kwargs)), custom_proxy=self.disable_proxy_result)
                else:
                    # return self.custom_proxy_handler(FunctionCallWrapper((self.func, args, kwargs)))
                    return AsyncFuture(future=FunctionCallWrapper((self.func, args, kwargs)), custom_proxy=self.custom_proxy_handler)


        if inspect.iscoroutinefunction(self.func):
            if not self.cooroutine:
                raise TypeError(f'The async or a coroutine function {self.func.__name__} may not be marked with a different decorator')
            self.rate_limiter.get_token()
            future = FunctionCallWrapper((self.func, args, kwargs))
        else:
            if self.cpu_bound:
                self.rate_limiter.get_token()
                future = self.process_executor.apply_async(
                    _multiprocess_target, (self.func.__module__, self.func.__name__), *args, **kwargs)
            else:
                self.rate_limiter.get_token()
                future = self.thread_executor.apply_async(self.func, *args, **kwargs)
        # logging.warning(future)

        if not self.custom_proxy_handler:
            return AsyncFuture(future=future)
        else:
            if self.cpu_bound or self.io_bound:
                future._process.daemon = True
            return AsyncFuture(future=future,custom_proxy=self.custom_proxy_handler)

    def __get__(self, instance, owner):
        def _call(*args, **kwargs):
            return self(instance, *args, **kwargs)

        functools.update_wrapper(_call, self.func)
        return _call


def _isfunction(obj):
    return callable(obj)


def _multiprocess_target(func_name, *args, **kwargs):
    # logging.warning(func_name)
    __import__(func_name[0])
    # print(AsyncFuse.unsync_functions)
    if func_name[0] == '__mp_main__':
        func_name = ('__main__',func_name[1])
    return AsyncFuse.unsync_functions[func_name](*args, **kwargs)


def AsyncFuseFactory(**flags):
    def _custom_unsync(*args, **kwargs):
        syn = AsyncFuse(*args, **kwargs)
        if 'cpu_bound' in flags.keys():
            syn.cpu_bound = True
        if 'io_bound' in flags.keys():
            syn.io_bound = True
        if 'cooroutine' in flags.keys():
            syn.cooroutine = True
        return syn
    return _custom_unsync


# T = TypeVar('T')

AsyncThread = AsyncFuseFactory(io_bound=True)
AsyncProcess = AsyncFuseFactory(cpu_bound=True)
AsyncCooroutine = AsyncFuseFactory(cooroutine=True)


class AsyncFuture():
    Disable = False
    def __str__(self) -> str:
        return f"future : {self.future},concurrent_Future={self.concurrent_future},"
    @staticmethod
    def from_value(value):
        future = AsyncFuture()
        future.set_result(value)
        return future

    def set_result(self, value):
        return self.future._loop.call_soon_threadsafe(lambda: self.future.set_result(value))

    def __init__(self, future=None,custom_proxy=None,disable=False):
        self.future = future
        self.disable = disable
        Disable = self.disable
        self.custom_proxy = custom_proxy
        if self.disable:
            return
        def callback(source, target):
                try:
                    asyncio.futures._chain_future(source, target)
                except Exception as exc:
                    if self.concurrent_future.set_running_or_notify_cancel():
                        self.concurrent_future.set_exception(exc)
                    raise


        # if not custom_proxy:
        #     self.custom_proxy = custom_proxy
        # else:
        #     self.custom_proxy = None

        if asyncio.iscoroutine(future):
            future = asyncio.ensure_future(future, loop=AsyncFuse.loop)

        if isinstance(future, concurrent.futures.Future):
            self.concurrent_future = future
            self.future = asyncio.Future(loop=AsyncFuse.loop)
            self.future._loop.call_soon_threadsafe(callback, self.concurrent_future, self.future)
        else:
            self.concurrent_future = concurrent.futures.Future()
            self.future = future or asyncio.Future(loop=AsyncFuse.loop)
            self.future._loop.call_soon_threadsafe(callback, self.future, self.concurrent_future)


    def done(self):
        return self.future.done() or self.concurrent_future.done()

    def __iter__(self):
        # if self.custom_proxy:
        #     return self.custom_proxy(self.future.__iter__()).result()
        # else:
        return self.future.__iter__()

    __await__ = __iter__

    def result(self, *args, **kwargs):
        if self.custom_proxy:
            # The asyncio Future may have completed before the concurrent one
            if self.disable:
                return self.custom_proxy(self.future).result()

            if self.future.done():
                return self.custom_proxy(self.future).result()

            # Don't allow waiting in the unsync.thread loop since it will deadlock
            if threading.current_thread() == AsyncFuse.thread and not self.concurrent_future.done():
                raise asyncio.InvalidStateError("Calling result() in an async method is not allowed")

            # Wait on the concurrent Future outside unsync.thread
            return self.custom_proxy(self.concurrent_future,*args,**kwargs).result()
        else:
            # The asyncio Future may have completed before the concurrent one
            if self.future.done():
                return self.future.result()

            # Don't allow waiting in the unsync.thread loop since it will deadlock
            if threading.current_thread() == AsyncFuse.thread and not self.concurrent_future.done():
                raise asyncio.InvalidStateError("Calling result() in an async method is not allowed")

            # Wait on the concurrent Future outside unsync.thread
            return self.concurrent_future.result(*args, **kwargs)

    @AsyncCooroutine(disable=Disable)
    async def then(self, continuation):
        # print(self)

        if not self.disable:

            if self.custom_proxy:
                self.custom_proxy(self.future).result()
            else:
                 await self

        # print(self)



        result = continuation(self.result())

        # print(result)
        if hasattr(result, '__await__'):
            return await result
        # print(self)
        return result


