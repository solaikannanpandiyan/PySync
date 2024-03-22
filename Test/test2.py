import asyncio
from multiprocessing import Process

from Scalar.unsynchronize2 import NonBlockingIO, BlockingIO
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(filename)s - (asctime)s - %(lineno)d  %(levelname)s - %(message)s')



# class NoDaemonProcess(multiprocessing.Process):
#     # make 'daemon' attribute always return False
#     def _get_daemon(self):
#         return False

#     def _set_daemon(self, value):
#         pass
#     daemon = property(_get_daemon, _set_daemon)

# # We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# # because the latter is only a wrapper function, not a proper class.


# class MyPool(multiprocessing.pool.Pool):
#     Process = NoDaemonProcess

@NonBlockingIO
async def enter(input):
    tasks = [async_function(0.1, i) for i in range(input)]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)


@NonBlockingIO
async def async_function(seconds, i):
    await asyncio.sleep(seconds)
    return f'Run concurrently cooroutine! {i}'



@BlockingIO
def non_async_function(seconds):
    time.sleep(0.1)
    return 'Run concurrently thread!'



# @unsync
# def non_async_function_cpu(input, batch):
#     tasks = [async_function(0.1, i) for i in range(input)]
#     # asyncio.run(enter(input))
#     print([task.result() for task in tasks])
#     return f'Run concurrently Process! batch: {batch}'

# @parallelize
# def processing():
#     non_async_function_cpu(100)




# @concurrent
# def work(input):
#     tasks = [non_async_function(0.1) for _ in range(input)]
#     print([task.result() for task in tasks])
#     # time.sleep(0.1)


# @synchronized
# def run():
#     for _ in range(10):
#         work(100000)




if __name__ == "__main__":
    start = time.time()
    tasks1 = []
    tasks2 = []
    x = Process(target=enter,name=enter.__name__,args=(10,))
    x.start()
    print("hello")
    x.join()
    # processing()
    # tasks1 = [non_async_function_cpu(2, i) for i in range(1000)]

    # with ProcessPoolExecutor(10) as th:
    #     thp = [th.submit(unsync,(non_async_function_cpu,1)) for _ in range(10)]
    #     [task.result() for task in thp]
    # tasks2 = [async_function(0.1) for _ in range(1000)]
    # tasks = tasks1 + tasks2
    # print([task.result() for task in tasks])
    print('Executed in {} seconds'.format(time.time() - start))
