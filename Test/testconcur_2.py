import time

from Scalar.concur2 import concurrent
# from unsynchronize2 import NonBlockingIO,CpuBound


# @NonBlockingIO
# async def enter(input):
#     tasks = [async_function(0.1, i) for i in range(input)]
#     results = await asyncio.gather(*tasks)
#     for result in results:
#         print(result)

# @NonBlockingIO
# async def async_function(seconds, i):
#     await asyncio.sleep(seconds)
#     # cpu_function(seconds)
#     return f'Run concurrently cooroutine! {i}'

# @CpuBound
# def cpu_function(seconds):
#     for _ in range(input):
#         for _ in range(input):
#             pass
#     print("cpu processing done")


@concurrent
def work(input):
    # x = enter(10)
    # x.result()
    print("work done")
    # tasks = [non_async_function(0.1) for _ in range(input)]
    # print([task.result() for task in tasks])
    # time.sleep(0.1)


def run():
    tasks = []
    for _ in range(1):
        tasks.append(work(10000))
    [tsk.get() for tsk in tasks]


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
