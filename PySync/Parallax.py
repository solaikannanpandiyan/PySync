import os
import signal
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types
from .config import default_limiter
from PySync.config import RateLimiter



def FunctionCallWrapper(x):
    f, args, kwargs = x
    result = Parallax.functions[f](*args, **kwargs)
    return result


def ParallaxFactory(constructor=None, apply_async=None):
        def _custom_Parallax(*args, **kwargs):
            parallel = Parallax(*args, **kwargs)
            if constructor is not None:
                parallel.engine = constructor
            if apply_async is not None:
                parallel.apply_async = apply_async
            return parallel
        return _custom_Parallax

class Parallax(object):
    functions = {}

    def __init__(self, *args, **kwargs):

        self.in_progress = False
        self.parallel_args = []
        self.parallel_kwargs = {}

        self.disable = False
        self.custom_proxy_handler = None
        self.time_interval = 0
        self.max_request = 0
        self.rate_limiter = RateLimiter
        self.kill = False

        if len(args) > 0 and hasattr(args[0], "__call__") and hasattr(args[0], "__name__"):
            self.setFunction(args[0])
        else:
            self.parallel_args = args
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
            self.parallel_kwargs = kwargs

        self.rate_limiter = self.rate_limiter(max_requests=self.max_request, per_seconds=self.time_interval)
        self.engine = ProcessPoolExecutor
        self.apply_async = lambda self, function, args: self.parallax_engine.submit(
            function, args)
        self.parallax_engine = None

    def __get__(self, *args):
        raise NotImplementedError(
            "Decorators from deco cannot be used on class methods")


    def setFunction(self, f):
        Parallax.functions[f.__name__] = f
        self.f_name = f.__name__
        self.__doc__ = f.__doc__
        self.__module__ = f.__module__

    def __call__(self, *args, **kwargs):

        if 'kill' in kwargs.keys():
            self.kill = kwargs.pop('kill',False)

        # if self.kill:
        #     self.parallax_engine.shutdown(wait=False)  # Don't wait for pending tasks to complete
        #     # Suppress output
        #     with open(os.devnull, 'w') as devnull:
        #         # Terminate the parent process without printing output
        #         # os.kill(os.getpid(), signal.SIGTERM, signal.SIG_DFL, stdout=devnull, stderr=devnull)
        #         os.kill(os.getpid(), signal.SIGTERM)

        if len(args) > 0 and isinstance(args[0], types.FunctionType):
            self.setFunction(args[0])
            return self

        self.in_progress = True

        if self.disable:
            if not self.custom_proxy_handler is None:
                return self.custom_proxy_handler(FunctionCallWrapper((self.f_name, args, kwargs)))
            else:
                return normal_result(FunctionCallWrapper((self.f_name, args, kwargs)))

        if self.parallax_engine is None:
            self.parallax_engine = self.engine(*self.parallel_args, **self.parallel_kwargs)

        self.rate_limiter.get_token()

        if not self.custom_proxy_handler is None:
            result = self.custom_proxy_handler( self.apply_async(
                self, FunctionCallWrapper, (self.f_name, args, kwargs) ) )
        else:
            result = ParallaxResult(self.apply_async(
                self, FunctionCallWrapper, (self.f_name, args, kwargs) ))
        return result


class ParallaxResult(object):
    def __init__(self, async_result):
        self.async_result = async_result

    def result(self):
        return self.async_result.result()

class normal_result(object):
    def __init__(self, normal_result):
        self.normal_result = normal_result

    def result(self):
        return self.normal_result

Thread = ParallaxFactory(constructor=ThreadPoolExecutor,
                                  apply_async=lambda self, function, args: self.parallax_engine.submit(function, args)
                                   )
Process = ParallaxFactory(constructor=ProcessPoolExecutor,
                                   apply_async=lambda self, function, args: self.parallax_engine.submit(function, args)
                                   )

# ThreadDaemon = Parallax.ParallaxFactory(constructor=ThreadPool,
#                                         apply_async=lambda self, function, args: self.parallax_engine.apply_async(function, args),
#                                         custom_proxy_handler=ParallaxDaemonResult)
# ProcessDaemon = Parallax.ParallaxFactory(constructor=Pool,
#                                          apply_async=lambda self, function, args: self.parallax_engine.apply_async(function, args),
#                                          custom_proxy_handler=ParallaxDaemonResult)


string = "   "
pattern = 
replacement =
new_string = re.sub(pattern, replacement, string)

