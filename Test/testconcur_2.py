import asyncio
import time
from PySync.AsyncFusion import AsyncCooroutine, AsyncProcess, AsyncThread






@AsyncProcess
def cpu_function(input):
    for _ in range(input):
        for _ in range(input):
            pass
    print("cpu processing done")

@AsyncCooroutine
async def async_function(seconds, i):
    cpu_function(1000)
    # cpu_function(seconds)
    return f'Run concurrently thread! {i}'

@AsyncCooroutine
async def async_cooroutine_function(input):
    tasks = [async_function(2, i) for i in range(input)]
    [task.result() for task in tasks]


def work(input):
    # x = enter(10)
    # x.result()
    print("work done")
    tasks = [async_cooroutine_function(5) for _ in range(input)]
    print([task.result() for task in tasks])
    # time.sleep(0.1)


def run():
    work(10)
    # tasks = []
    # for _ in range(1):
    #     tasks.append(work(10))
    # [tsk.result() for tsk in tasks]


if __name__ == "__main__":
    start = time.time()
    tasks2 = []
    run()

    # x.join()
    # with ProcessPoolExecutor(3) as x:
    #     res = x.submit(run, ())


    # run()

    # processing()
    # tasks1 = [non_async_function_cpu(2, i) for i in range(1000)]

    # with ProcessPoolExecutor(10) as th:
    #     thp = [th.submit(unsync,(non_async_function_cpu,1)) for _ in range(10)]
    #     [task.result() for task in thp]
    # tasks2 = [async_function(0.1) for _ in range(1000)]
    # tasks = tasks1 + tasks2
    # print([task.result() for task in tasks])
    print('Executed in {} seconds'.format(time.time() - start))
