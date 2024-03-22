import asyncio
from unsync import unsync
from Scalar.concur import concurrent
import time


@unsync
async def non_async_function(seconds):
    await asyncio.sleep(seconds)
    return 'Run concurrently!'


@concurrent
def work2(input):
    for _ in range(input):
        for _ in range(input):
            pass
    print("work done")


@concurrent
def work(input):
    for _ in range(input):
        for _ in range(input):
            pass
    work(input)
    print("work done")
    # tasks = [non_async_function(0.1) for _ in range(input)]
    # print([task.result() for task in tasks])
    # time.sleep(0.1)


def run():
    for _ in range(3):
        work(100)
    work.wait()


if __name__ == "__main__":
    start = time.time()
    run()
    # tasks = [non_async_function(0.1) for _ in range(100000)]
    # print([task.result() for task in tasks])
    print('Executed in {} seconds'.format(time.time() - start))
