import asyncio
import concurrent
import functools
import inspect
import os
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Thread
from typing import Generic, TypeVar
from .config import default_limiter, RateLimiter
# from .config import getconfig
import logging


# logging.basicConfig(level=logging.INFO,format='%(filename)s - (asctime)s - %(lineno)d  %(levelname)s - %(message)s')

def CooroutineCallWrapper(x):
    f, limiter, args, kwargs = x
    limiter.get_token()
    CooroutineTask = f(*args, **kwargs)
    return CooroutineTask

class Async_Meta(type):
    def _init_loop(cls):
        print("Async_Meta __init__ called")
        print(vars(cls))
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

    # @property
    # def process_executor(cls):
    #     # print("Async_Meta process_exec called")
    #     if getattr(cls, '_process_executor', None) is None:
    #         cls._process_executor = concurrent.futures.ProcessPoolExecutor(cls.worker_count)
    #     return cls._process_executor
    #
    # @property
    # def thread_executor(cls):
    #     # print("Async_Meta process_exec called")
    #     if getattr(cls, '_thread_executor', None) is None:
    #         cls._thread_executor = concurrent.futures.ThreadPoolExecutor(cls.worker_count)
    #     return cls._thread_executor


class AsyncFuse(object, metaclass=Async_Meta):
    worker_count = os.cpu_count()
    async_fuse_functions = {}

    @staticmethod
    def _thread_target(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def __init__(self, *args, **kwargs):
        # print("AsyncFuse __init__ called")
        self.fuseargs = []
        self.fusekwargs = {}

        self.cpu_bound = False
        self.io_bound = False
        self.cooroutine = False

        self.custom_proxy_handler = None
        self.time_interval = 0
        self.max_request = 0
        self.rate_limiter = RateLimiter
        self.process_executor = ProcessPoolExecutor
        self.thread_executor = ThreadPoolExecutor
        # self.max_worker = os.cpu_count()
        if len(args) == 1 and _isfunction(args[0]):

            self._set_func(args[0])
            print("AsyncFuse set_func called")
            print("args : ", args)
            print("kwargs : ", kwargs)
        else:
            print("AsyncFuse args,kwargs called")
            print("args : ", args)
            print("kwargs : ", kwargs)
            self.fuseargs = args

            if 'custom_proxy_handler' in kwargs.keys():
                self.custom_proxy_handler = kwargs.pop('custom_proxy_handler')
            # if 'max_worker' in kwargs.keys():
            #     self.max_worker = kwargs.pop('max_worker')

            if 'io_bound' in kwargs.keys():
                self.io_bound = kwargs.pop('io_bound', False)
            if 'cooroutine' in kwargs.keys():
                self.cooroutine = kwargs.pop('cooroutine', False)
            if 'cpu_bound' in kwargs.keys():
                self.cpu_bound = kwargs.pop('cpu_bound', False)

            if 'disable' in kwargs.keys():
                self.disable = kwargs.pop('disable', False)
            if 'max_request' in kwargs.keys():
                self.max_request = kwargs.pop('max_request')
            if 'time_interval' in kwargs.keys():
                self.time_interval = kwargs.pop('time_interval')
            if 'rate_limiter' in kwargs.keys():
                self.rate_limiter = kwargs.pop('rate_limiter')

            self.fusekwargs = kwargs
            self.func = None

        # AsyncFuse.worker_count =self.max_worker
        self.rate_limiter = self.rate_limiter(max_requests=self.max_request, per_seconds=self.time_interval)

    # @property
    # def cpu_bound(self):
    #     return 'cpu_bound' in self.kwargs and self.kwargs['cpu_bound']
    #
    # @property
    # def io_bound(self):
    #     return 'io_bound' in self.kwargs and self.kwargs['io_bound']
    #
    # @property
    # def cooroutine(self):
    #     return 'cooroutine' in self.kwargs and self.kwargs['cooroutine']

    def _set_func(self, func):
        assert _isfunction(func)
        self.func = func
        functools.update_wrapper(self, func)
        # On Windows/Mac MP turns the main module into __mp_main__ in multiprocess targets
        module = "__main__" if func.__module__ == "__mp_main__" else func.__module__
        AsyncFuse.async_fuse_functions[(module, func.__name__)] = func

    def __call__(self, *args, **kwargs):
        # print(self.func)
        # print(self.io_bound)
        # print(self.cooroutine)
        # print(self.cpu_bound)
        # print(args)
        # print(kwargs)

        # print("event loop",AsyncFuse.loopid)

        if self.func is None:
            self._set_func(args[0])
            return self

        if inspect.iscoroutinefunction(self.func):
            if self.cpu_bound:
                raise TypeError('The CPU bound unsync function %s may not be async or a coroutine' % self.func.__name__)
            future = CooroutineCallWrapper((self.func, self.rate_limiter, args, kwargs))
        else:
            if self.cpu_bound:
                self.rate_limiter.get_token()
                future = self.process_executor(*self.fuseargs, **self.fusekwargs).submit(
                    _multiprocess_target, (self.func.__module__, self.func.__name__), *args, **kwargs)
            else:
                self.rate_limiter.get_token()
                future = self.thread_executor(*self.fuseargs, **self.fusekwargs).submit(self.func, *args, **kwargs)
        # logging.warning(future)
        return AsyncFuture(future)

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
    return AsyncFuse.async_fuse_functions[func_name](*args, **kwargs)


def AsyncFactory(**flags):
    def _custom_unsync(*args, **kwargs):
        syn = AsyncFuse(*args, **kwargs)
        # for k, v in flags.items():
        #     syn.kwargs[k] = v
        return syn

    return _custom_unsync


T = TypeVar('T')

AsyncThread = AsyncFactory(io_bound=True)
AsyncProcess = AsyncFactory(cpu_bound=True)
AsyncCooroutine = AsyncFactory(cooroutine=True)


class normal_result(object):
    def __init__(self, normal_result):
        self.normal_result = normal_result

    def result(self):
        return self.normal_result

class AsyncFuture(Generic[T]):
    DISABLE = False
    def __str__(self) -> str:
        return f"future : {self.future},concurrent_Future={self.concurrent_future},"

    @staticmethod
    def from_value(value):
        future = AsyncFuture()
        future.set_result(value)
        return future

    def set_result(self, value):
        return self.future._loop.call_soon_threadsafe(lambda: self.future.set_result(value))

    def __init__(self, future=None):
        def callback(source, target):
            try:
                asyncio.futures._chain_future(source, target)
            except Exception as exc:
                if self.concurrent_future.set_running_or_notify_cancel():
                    self.concurrent_future.set_exception(exc)
                raise

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
        return self.future.__iter__()

    __await__ = __iter__

    def result(self, *args, **kwargs) -> T:
        # The asyncio Future may have completed before the concurrent one
        if self.future.done():
            return self.future.result()

        # Don't allow waiting in the unsync.thread loop since it will deadlock
        if threading.current_thread() == AsyncFuse.thread and not self.concurrent_future.done():
            raise asyncio.InvalidStateError("Calling result() in an async method is not allowed")

        # Wait on the concurrent Future outside unsync.thread
        return self.concurrent_future.result(*args, **kwargs)



    @AsyncCooroutine()
    async def then(self, continuation):

        # print(self)
        await self
        # print(self)

        result = continuation(self.result())
        # print(result)
        if hasattr(result, '__await__'):
            return await result
        # print(self)
        return result

