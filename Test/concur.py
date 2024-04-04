from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import types
import time


def concWrapper(x):
    start = time.time()
    f, args, kwargs = x
    result = concurrent.functions[f](*args, **kwargs)
    print(f'Function {f} Executed in {time.time() - start} seconds')
    return result
    # print("result",result)


class concurrent(object):
    functions = {}

    @staticmethod
    def custom(constructor=None, apply_async=None):
        @staticmethod
        def _custom_concurrent(*args, **kwargs):
            conc = concurrent(*args, **kwargs)
            if constructor is not None:
                conc.conc_constructor = constructor
            if apply_async is not None:
                conc.apply_async = apply_async
            return conc
        return _custom_concurrent

    def __init__(self, *args, **kwargs):
        # print("init now")
        # print("self: ", self)
        # print("self functions: ", self.functions)
        # print("self concurrency: ", self.concurrency)
        # print("input conc args: ", args)
        # print("input kwargs: ", kwargs)
        self.in_progress = False
        self.conc_args = []
        self.conc_kwargs = {}
        if len(args) > 0 and hasattr(args[0], "__call__") and hasattr(args[0], "__name__"):
            self.setFunction(args[0])
        else:
            self.conc_args = args
            self.conc_kwargs = kwargs
        self.conc_constructor = ProcessPoolExecutor
        self.apply_async = lambda self, function, args: self.concurrency.submit(function, args)
        self.concurrency = None
        # print("self: ", self)
        # print("self functions: ", self.functions)
        # print("self concurrency: ", self.concurrency)
        # print("self conc args: ", self.conc_args)
        # print("self kwargs: ", self.conc_kwargs)

    def __get__(self, *args):
        raise NotImplementedError(
            "Decorators from deco cannot be used on class methods")

    def setFunction(self, f):
        concurrent.functions[f.__name__] = f
        self.f_name = f.__name__
        self.__doc__ = f.__doc__
        self.__module__ = f.__module__

    def __call__(self, *args, **kwargs):
        # print("called now")
        # print("self: ",self)
        # print("self functions: ",self.functions)
        # print("self concurrency: ",self.concurrency)
        # print("input args: ",args)
        # print("input kwargs: ",kwargs)
        if len(args) > 0 and isinstance(args[0], types.FunctionType):
            self.setFunction(args[0])
            return self

        self.in_progress = True

        if self.concurrency is None:
            # print("construction:",self.conc_constructor)
            # print(*self.conc_args )
            # print(**self.conc_kwargs)
            self.concurrency = self.conc_constructor(*self.conc_args, **self.conc_kwargs)
            # print("construction:", self.concurrency)
        args = list(args)
        result = ConcurrentResult(self.apply_async(
            self, concWrapper, (self.f_name, args, kwargs) ))
        # print("self: ", self)
        # print("self functions: ", self.functions)
        # print("self concurrency: ", self.concurrency)
        # print("self conc args: ", self.conc_args)
        # print("self kwargs: ", self.conc_kwargs)
        # print("self result: ", result)
        return result



Thread = concurrent.custom(ThreadPoolExecutor)
Processor= concurrent.custom(ProcessPoolExecutor)


class ConcurrentResult(object):
    def __init__(self, async_result):
        self.async_result = async_result

    def get(self):
        # return self.async_result.get(3e+6)
        return self.async_result.result()

    def result(self):
        return self.get()

