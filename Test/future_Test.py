import asyncio
import concurrent


async def func():
    await asyncio.sleep(1)
    print("hello")
    return 10

# def main():
#     print('hello')

if __name__ == "__main__":
    # asyncio.run(func())
    loop = asyncio.new_event_loop()
    # y = asyncio.ensure_future(func())
    future = asyncio.ensure_future(func(), loop=loop)
    concurrent_future = concurrent.futures.Future()
    loop.call_soon_threadsafe(asyncio.futures._chain_future(future,concurrent_future))
    loop.run_until_complete(future)
    print(future.result())
    print(concurrent_future.result())
    # print(x)
    # print(y)