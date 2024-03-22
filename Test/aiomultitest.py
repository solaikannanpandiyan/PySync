import asyncio
from aiomultiprocess import Pool

async def request(i):
    await asyncio.sleep(1)
    print(f"request {i} completed!")
    return

async def get(i):
    return await request(i)

async def main():
    urls = [i for i in range(100000)]
    async with Pool(10) as pool:
        async for result in pool.map(get, urls):
            pass

if __name__ == '__main__':
    # Python 3.7
    asyncio.run(main())
