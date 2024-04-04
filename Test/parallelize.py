import sys
from concurrent.futures import process
from multiprocessing import current_process
import asyncio

# from unsync import unsync
# from Scalar.concur3 import concurrent
# from PySync import Thread, Process

from PySync.config import set_config, RateLimiter
from PySync.AsyncFusion_2 import AsyncCooroutine, AsyncProcess, AsyncThread
from PySync.Parallax import Process,Thread
import time
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('example.log')
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# logging.disable(logging.ERROR)

class customer_exception_handler():
    def __init__(self, custom_object, *args, **kwargs):
        self.custom_object = custom_object
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        return self.custom_object.__iter__()

    __await__ = __iter__

    async def result(self):
        try:
            if not asyncio.iscoroutine(self.custom_object):
                self.custom_object.result(*self.args, **self.kwargs)
            else:
                await self

        except Exception as ex:
            print(f"{ex}")
            return -1

# class normal_result(object):
#     def __init__(self, normal_result, *args, **kwargs):
#         self.normal_result = normal_result
#         self.args = args
#         self.kwargs = kwargs
#     def result(self):
#         try:
#             return self.normal_result.result(*self.args, **self.kwargs)
#         except Exception as ex:
#             logging.info(f'{ex}')
#             return 1


# @AsyncProcess(max_workers=10)
# def proc_function_2(seconds):
#     for _ in range(1000):
#         for _ in range(1000):
#             pass
#     logging.info(f'Run {seconds} concurrently process!')
#     return seconds

# def processor_function(seconds):
#     # report if daemon process
#     time.sleep(seconds)
#     return 'Run concurrently process!'



# @Process(1)
# def work(input,i):
#     # for _ in range(input):
#     #     for _ in range(input):
#     #         pass
#     # tasks = [processor_function(1) for _ in range(10)]
#     # print([task.result() for task in tasks])
#     tasks1 = [async_function(input+i*input) for i in range(input)]
#     [task.result() for task in tasks1]
#     logging.info(f"work {i} completed")
#     return 1
#     # return len(tasks1)
#     # time.sleep(0.1)




@AsyncCooroutine(custom_proxy_handler=customer_exception_handler)
async def async_function(i):
    await asyncio.sleep(1)
    logging.info(f'Run {i} concurrently cooroutine!')
    # [await non_async_function(i) for i in range(1000)]
    # await proc_function(i)
    raise Exception(f"raising a async_function {i} exception")
    return i
#
# #
@AsyncThread(1000,custom_proxy_handler=customer_exception_handler)
def non_async_function(seconds):
    time.sleep(1)
    logging.info(f'Run {seconds} concurrently thread!')
    raise Exception(f"raising a non_async_function {seconds} exception")
    return seconds


@AsyncProcess(100,custom_proxy_handler=customer_exception_handler)
def proc_function(seconds):
    for _ in range(1000):
        for _ in range(1000):
            pass
    logging.info(f'Run {seconds} concurrently process!')
    raise Exception(f"raising a proc_function {seconds} exception")
    return seconds

def printer(*args):
    logging.info(f"value {args}")
    return args

if __name__ == "__main__":
    start = time.time()
    tasks1 = []
    tasks2 = []
    tasks3 = []
    tasks = []
    # tasks1 = [ work(100000,i) for i in range(10) ]
    # tasks1 = [async_function(i) for i in range(3)]
    # tasks2 = [non_async_function(i) for i in range(3)]
    # tasks3 = [proc_function(i) for i in range(3)]
    #
    # # with ThreadPoolExecutor(1000) as th:
    # #     thp = [th.submit(non_async_function, 0.1) for _ in range(1000)]
    # #     print([task.result() for task in thp])
    # tasks1 = [async_function(i) for i in range(10000)]
    # tasks2 = [non_async_function(i) for i in range(1000)]
    # tasks3 = [proc_function(i) for i in range(100)]
    # tasks2 = [non_async_function(i) for i in range(2)]
    # [ print(task.result()) for task in tasks1 + tasks2 + tasks3]
    # # print(tasks1)

    tasks = [async_function(i).then(non_async_function).then(proc_function) for i in range(5)]

    # tasks = [async_function(i).then(non_async_function).then(proc_function) for i in range(5)]
    m = [task.result() for task in tasks1 + tasks2 + tasks3 + tasks]

    logging.critical('Executed in {} seconds'.format(time.time() - start))
