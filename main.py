import asyncio

from websuckets import WebSuckets


async def main():
    app = WebSuckets()
    task = asyncio.create_task(app("localhost",10002))
    await task


if __name__ == '__main__':
    asyncio.run(main())
