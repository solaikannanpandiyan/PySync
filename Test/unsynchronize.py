# import asyncio
# import concurrent
# import functools
# import inspect
# import threading
# from threading import Thread
# from typing import Generic, TypeVar
# import logging
# logging.basicConfig(level=logging.INFO,format='%(filename)s - (asctime)s - %(lineno)d  %(levelname)s - %(message)s')
#
#
#
# class unsync_meta(type):
#     def _init_loop(cls):
#         print("this only be printed only once")
#         cls._loop = asyncio.new_event_loop()
#         cls._thread = Thread(target=cls._thread_target, args=(cls._loop,), daemon=True)
#         cls._thread.start()
#
#     @staticmethod
#     def _thread_target(loop):
#         asyncio.set_event_loop(loop)
#         loop.run_forever()
#
#     @property
#     def loop(cls):
#         if getattr(cls, '_loop', None) is None:
#             unsync_meta._init_loop(cls)
#         return cls._loop
#
#     @property
#     def thread(cls):
#         if getattr(cls, '_thread', None) is None:
#             unsync_meta._init_loop(cls)
#         return cls._thread
#
#     @property
#     def process_executor(cls):
#         if getattr(cls, '_process_executor', None) is None:
#             cls._process_executor = concurrent.futures.ProcessPoolExecutor()
#         return cls._process_executor
#
#
# class NonBlockingIO(object, metaclass=unsync_meta):
#     thread_executor = concurrent.futures.ThreadPoolExecutor()
#     process_executor = None
#     unsync_functions = {}
#
#     def __init__(self, *args, **kwargs):
#         self.args = []
#         self.kwargs = {}
#         if len(args) == 1 and _isfunction(args[0]):
#             self._set_func(args[0])
#         else:
#             self.args = args
#             self.kwargs = kwargs
#             self.func = None
#
#     def _set_func(self, func):
#         assert _isfunction(func)
#         self.func = func
#         functools.update_wrapper(self, func)
#         # On Windows/Mac MP turns the main module into __mp_main__ in multiprocess targets
#         module = "__main__" if func.__module__ == "__mp_main__" else func.__module__
#         NonBlockingIO.unsync_functions[(module, func.__name__)] = func
#
#     def __call__(self, *args, **kwargs):
#         if self.func is None:
#             self._set_func(args[0])
#             return self
#         if inspect.iscoroutinefunction(self.func):
#             future = self.func(*args, **kwargs)
#         else:
#             raise TypeError('The decorated function %s may not be async or a coroutine' % self.func.__name__)
#         logging.warning(future)
#         return Unfuture(future)
#
#     def __get__(self, instance, owner):
#         def _call(*args, **kwargs):
#             return self(instance, *args, **kwargs)
#         functools.update_wrapper(_call, self.func)
#         return _call
#
#
# class BlockingIO(object, metaclass=unsync_meta):
#     thread_executor = concurrent.futures.ThreadPoolExecutor()
#     process_executor = None
#     unsync_functions = {}
#
#     def __init__(self, *args, **kwargs):
#         self.args = []
#         self.kwargs = {}
#         if len(args) == 1 and _isfunction(args[0]):
#             self._set_func(args[0])
#         else:
#             self.args = args
#             self.kwargs = kwargs
#             self.func = None
#
#     def _set_func(self, func):
#         assert _isfunction(func)
#         self.func = func
#         functools.update_wrapper(self, func)
#         # On Windows/Mac MP turns the main module into __mp_main__ in multiprocess targets
#         module = "__main__" if func.__module__ == "__mp_main__" else func.__module__
#         BlockingIO.unsync_functions[(module, func.__name__)] = func
#
#     def __call__(self, *args, **kwargs):
#         if self.func is None:
#             self._set_func(args[0])
#             return self
#         if inspect.iscoroutinefunction(self.func):
#             raise TypeError('The decorated function %s is async or a coroutine (Expected a blocking io bound)' % self.func.__name__)
#
#         future = BlockingIO.thread_executor.submit(self.func, *args, **kwargs)
#
#         logging.warning(future)
#         return Unfuture(future)
#
#     def __get__(self, instance, owner):
#         def _call(*args, **kwargs):
#             return self(instance, *args, **kwargs)
#
#         functools.update_wrapper(_call, self.func)
#         return _call
#
#
#
# class CpuBound(object, metaclass=unsync_meta):
#     thread_executor = concurrent.futures.ThreadPoolExecutor()
#     process_executor = None
#     unsync_functions = {}
#
#     def __init__(self, *args, **kwargs):
#         self.args = []
#         self.kwargs = {}
#         if len(args) == 1 and _isfunction(args[0]):
#             self._set_func(args[0])
#         else:
#             self.args = args
#             self.kwargs = kwargs
#             self.func = None
#
#     def _set_func(self, func):
#         assert _isfunction(func)
#         self.func = func
#         functools.update_wrapper(self, func)
#         # On Windows/Mac MP turns the main module into __mp_main__ in multiprocess targets
#         module = "__main__" if func.__module__ == "__mp_main__" else func.__module__
#         CpuBound.unsync_functions[(module, func.__name__)] = func
#
#     def __call__(self, *args, **kwargs):
#         if self.func is None:
#             self._set_func(args[0])
#             return self
#
#         if inspect.iscoroutinefunction(self.func):
#             raise TypeError('The decorated function %s is async or a coroutine (Expected a cpu bound)' % self.func.__name__)
#
#         future = CpuBound.process_executor.submit(_multiprocess_target,self, (self.func.__module__, self.func.__name__), *args, **kwargs)
#
#         logging.warning(future)
#         return Unfuture(future)
#
#     def __get__(self, instance, owner):
#         def _call(*args, **kwargs):
#             return self(instance, *args, **kwargs)
#
#         functools.update_wrapper(_call, self.func)
#         return _call
#
# def _isfunction(obj):
#     return callable(obj)
#
#
# def _multiprocess_target(self,func_name, *args, **kwargs):
#     logging.warning(func_name)
#     __import__(func_name[0])
#     return self.unsync_functions[func_name](*args, **kwargs)
#
#
# T = TypeVar('T')
#
#
# class Unfuture(Generic[T]):
#     @staticmethod
#     def from_value(value):
#         future = Unfuture()
#         future.set_result(value)
#         return future
#
#     def __init__(self, future=None):
#         def callback(source, target):
#             try:
#                 asyncio.futures._chain_future(source, target)
#             except Exception as exc:
#                 if self.concurrent_future.set_running_or_notify_cancel():
#                     self.concurrent_future.set_exception(exc)
#                 raise
#
#         if asyncio.iscoroutine(future):
#             future = asyncio.ensure_future(future, loop=NonBlockingIO.loop)
#
#         if isinstance(future, concurrent.futures.Future):
#             self.concurrent_future = future
#             self.future = asyncio.Future(loop=NonBlockingIO.loop)
#             self.future._loop.call_soon_threadsafe(callback, self.concurrent_future, self.future)
#         else:
#             self.concurrent_future = concurrent.futures.Future()
#             self.future = future or asyncio.Future(loop=NonBlockingIO.loop)
#             self.future._loop.call_soon_threadsafe(callback, self.future, self.concurrent_future)
#
#     def __iter__(self):
#         return self.future.__iter__()
#
#     __await__ = __iter__
#
#     def result(self, *args, **kwargs) -> T:
#         # The asyncio Future may have completed before the concurrent one
#         if self.future.done():
#             return self.future.result()
#         # Don't allow waiting in the unsync.thread loop since it will deadlock
#         if threading.current_thread() == NonBlockingIO.thread and not self.concurrent_future.done():
#             raise asyncio.InvalidStateError("Calling result() in an unsync method is not allowed")
#         # Wait on the concurrent Future outside unsync.thread
#         return self.concurrent_future.result(*args, **kwargs)
#
#     def done(self):
#         return self.future.done() or self.concurrent_future.done()
#
#     def set_result(self, value):
#         return self.future._loop.call_soon_threadsafe(lambda: self.future.set_result(value))
#
#     @NonBlockingIO
#     async def then(self, continuation):
#         await self
#         result = continuation(self.result())
#         if hasattr(result, '__await__'):
#             return await result
#         return result
#
