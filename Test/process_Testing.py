import time
import types
from concurrent.futures import ProcessPoolExecutor
from Innovation import Thread, Process
# from concurrent.futures.process import ProcessPoolExecutor

class deco():
    def __init__(self, *args, **kwargs):
        print("init")
        print(args)
        print(kwargs)

    def __call__(self, *args, **kwargs):
        print("calling")
        print(args)
        print(kwargs)
        if len(args) > 0 and isinstance(args[0], types.FunctionType):

            return self


@Process
def function(x):
    print("executing")
    time.sleep(x)
    print("execution completed")
    return 1

@Process
def function1(x):
    print("executing")
    time.sleep(x)
    print("execution completed")
    return 2

@Thread
def function2(i):
    print("executing")
    time.sleep(30)
    print("execution completed")
    return i

def wrapper(x):
    x[0](x[1])

if __name__ == '__main__':
    x = [function2(i) for i in range(3)]
    time.sleep(15)
    [print(res.result()) for res in x]




    # args = (function,3)
    # x = ProcessPoolExecutor(max_workers=10).submit(wrapper,args)


    # time.sleep(1)
    # print("hello")
    # print("how are you")
    # x.result()



