
import asyncio
from backend.producers.base.producer import TrafficProducer

async def main():
    producer = TrafficProducer()
    await producer.produce(interval=0.001)

if __name__ == '__main__':
    asyncio.run(main())
