from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types


def FunctionCallWrapper(x):
    f, args, kwargs = x
    result = Parallax.functions[f](*args, **kwargs)
    return result

class Parallax(object):
    functions = {}
    @staticmethod
    def ParallaxFactory(constructor=None, apply_async=None):
        @staticmethod
        def _custom_Parallax(*args, **kwargs):
            parallel = Parallax(*args, **kwargs)
            if constructor is not None:
                parallel.engine = constructor
            if apply_async is not None:
                parallel.apply_async = apply_async
            return parallel
        return _custom_Parallax

    def __init__(self, *args, **kwargs):
        self.in_progress = False
        self.parallel_args = []
        self.parallel_kwargs = {}
        if len(args) > 0 and hasattr(args[0], "__call__") and hasattr(args[0], "__name__"):
            self.setFunction(args[0])
        else:
            self.parallel_args = args
            self.parallel_kwargs = kwargs
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
        if len(args) > 0 and isinstance(args[0], types.FunctionType):
            self.setFunction(args[0])
            return self
        self.in_progress = True
        if self.parallax_engine is None:
            self.parallax_engine = self.engine(*self.parallel_args, **self.parallel_kwargs)
        args = list(args)
        result = ParallaxResult(self.apply_async(
            self, FunctionCallWrapper, (self.f_name, args, kwargs) ))
        return result

Thread = Parallax.ParallaxFactory(ThreadPoolExecutor)
Process = Parallax.ParallaxFactory(ProcessPoolExecutor)

class ParallaxResult(object):
    def __init__(self, async_result):
        self.async_result = async_result

    def result(self):
        return self.async_result.result()

