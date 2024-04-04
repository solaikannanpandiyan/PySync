# import asyncio
#
# from Scalar.concur import concurrent
# import time
#
#
# @unsync
# async def async_function(seconds):
#     await asyncio.sleep(seconds)
#     return 'Run concurrently!'
#
#
# @unsync(cpu_bound=True)
# def cpu_bound_function(times):
#     for i in range(times):
#         pass
#     return 'Run in parallel!'
#
#
# # # Could also be applied as a decorator above
# # unsync_cpu_bound_function = unsync(cpu_bound=True)(cpu_bound_function)
#
# @concurrent()
# def work(input):
#     task1 = [async_function(0.1) for _ in range(input)]
#     task2 = [cpu_bound_function(2) for _ in range(input)]
#     tasks = task1 + task2
#     print([task.result() for task in tasks])
#     # time.sleep(0.1)
#
#
# def run():
#     for _ in range(10):
#         work(2)
#     work.wait()
#
#
# if __name__ == "__main__":
#     start = time.time()
#     run()
#     # tasks = [non_async_function(0.1) for _ in range(100000)]
#     # print([task.result() for task in tasks])
#     print('Executed in {} seconds'.format(time.time() - start))
