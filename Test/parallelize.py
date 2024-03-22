from concurrent.futures import process
from multiprocessing import current_process
import asyncio
from unsync import unsync
from Scalar.concur3 import concurrent
from Innovation import Thread, Process
from Innovation import AsyncCooroutine, AsyncProcess, AsyncThread
import time


@AsyncCooroutine
async def async_function(i):
    await asyncio.sleep(1)
    return f'Run {i} concurrently cooroutine!'


@AsyncThread
def non_async_function(seconds):
    time.sleep(0.1)
    return 'Run concurrently thread!'


@AsyncProcess
def proc_function(seconds):
    # get the current process

    # report if daemon process
    print(f'Daemon process: {process.daemon}')
    for _ in range(10000):
        for _ in range(10000):
            pass
    return 'Run concurrently process!'



def processor_function(seconds):
    # get the current process
    process = current_process()
    # report if daemon process
    time.sleep(seconds)
    return 'Run concurrently process!'



@Process
def work(input,i):
    # for _ in range(input):
    #     for _ in range(input):
    #         pass
    # tasks = [processor_function(1) for _ in range(10)]
    # print([task.result() for task in tasks])
    tasks1 = [async_function(i) for i in range(input)]
    [print(task.result()) for task in tasks1]
    print(f"work {i} completed")
    return len(tasks1)
    # time.sleep(0.1)


def run():
    for _ in range(2):
        work(1000)



if __name__ == "__main__":
    start = time.time()
    tasks1 = []
    tasks2 = []
    tasks1 = [ work(1000,i) for i in range(10) ]

    # with ThreadPoolExecutor(1000) as th:
    #     thp = [th.submit(non_async_function, 0.1) for _ in range(1000)]
    #     print([task.result() for task in thp])
    # tasks2 = [async_function(1) for _ in range(1000000)]
    # run()
    [ print(task.result()) for task in tasks1 ]
    print(tasks1)
    print('Executed in {} seconds'.format(time.time() - start))
