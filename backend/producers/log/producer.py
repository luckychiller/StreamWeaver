import asyncio
from backend.producers.base.producer import ServerLogProducer

async def main():
    producer = ServerLogProducer()
    await producer.produce(interval=0.001)

if __name__ == '__main__':
    asyncio.run(main())