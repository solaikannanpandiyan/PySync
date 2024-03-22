from Scalar.unsychronize import unsync
import time
import asyncio

@unsync
async def async_function(seconds, i):
    await asyncio.sleep(seconds)
    return f'Run concurrently cooroutine! {i}'


@unsync(cpu_bound=True)
def non_async_function_cpu(batch):
    for _ in range(100000):
        for _ in range(1000):
            pass
    return f'Run concurrently Process! batch: {batch}'


@unsync
def non_async_function_thread(seconds,i):
    time.sleep(seconds)
    return f'Run concurrently in thread! {i}'

if __name__ == "__main__":
    start = time.time()
    tasks = []
    tasks.append(non_async_function_thread(2,1))
    tasks.append(non_async_function_cpu(1))
    tasks.append(async_function(2, 1))
    print([task.result() for task in tasks])
    print('Executed in {} seconds'.format(time.time() - start))
