import asyncio
from backend.producers.base.producer import SocialMediaProducer

async def main():
    producer = SocialMediaProducer()
    await producer.produce(interval=0.001)

if __name__ == '__main__':
    asyncio.run(main())