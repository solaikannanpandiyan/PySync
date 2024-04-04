import time
import types
from concurrent.futures import ProcessPoolExecutor
# from concurrent.futures.process import ProcessPoolExecutor
from PySync.Parallax import Process,Thread
from PySync.config import RateLimiter

TOKEN_COUNT = 1
TIME_INTERVAL = 1
limiter = RateLimiter(max_requests=TOKEN_COUNT, per_seconds=TIME_INTERVAL)

@Process
def function(x):
    print("executing")
    time.sleep(x)
    print("execution completed")
    return 1

@Thread(1000)
def function1(i):
    print(f"executing {i}")
    time.sleep(5)
    print(f"execution {i} completed")
    return


# disable True or False | default = False
# custom_proxy_handler None or Proxy object | default = None
# rate_limiter ratelimiter object | default = None


@Thread(1000)
def function2(i):
    print(f"executing {i}")
    time.sleep(1)
    print(f"execution {i} completed")
    return

def wrapper(x):
    x[0](x[1])

if __name__ == '__main__':
    start = time.time()
    # x = [function2(i) for i in range(1000)]
    x = [function2(i) for i in range(1000)]
    # time.sleep(2)
    [res.result() for res in x]



    # args = (function,3)
    # x = ProcessPoolExecutor(max_workers=10).submit(wrapper,args)


    # time.sleep(1)
    # print("hello")
    # print("how are you")
    # x.result()
    print('Executed in {} seconds'.format(time.time() - start))


