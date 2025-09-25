import asyncio
from backend.producers.base.producer import StockTradeProducer

async def main():
    producer = StockTradeProducer()
    await producer.produce(interval=0.001)

if __name__ == '__main__':
    asyncio.run(main())