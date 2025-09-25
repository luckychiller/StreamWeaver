"""
Base producer implementation using Template Method and Abstract Factory patterns.
Design Pattern: Template Method - Defines the skeleton of data production algorithm.
Design Pattern: Abstract Factory - Creates families of related data generators.
"""
import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from ...common.kafka_client import KafkaProducerClient
from ...common.config import Config


class BaseProducer(ABC):
    """
    Abstract base class for all data producers.
    Template Method pattern: produce() defines the algorithm, subclasses implement generate_data().
    """
    def __init__(self, topic: str):
        self.topic = topic
        self.kafka_producer = KafkaProducerClient()

    @abstractmethod
    def generate_data(self) -> dict:
        """Abstract method for data generation - implemented by subclasses."""
        pass

    async def produce(self, interval: float = 1.0):
        """
        Template method: Main production loop.
        Generates data, sends to Kafka, sleeps with random jitter.
        """
        while True:
            data = self.generate_data()
            key = self.get_key(data)
            self.kafka_producer.send_message(self.topic, data, key)
            print(f"Produced to {self.topic}: {data}")
            jitter = interval * 0.2
            sleep_duration = random.uniform(interval - jitter, interval + jitter)    
            await asyncio.sleep(sleep_duration)

    def get_key(self, data: dict) -> str:
        """Hook method: Can be overridden for custom partitioning keys."""
        return None

class StockTradeProducer(BaseProducer):
    """
    Concrete implementation for stock trade data production.
    Generates realistic stock trading data with timestamps and market symbols.
    """
    def __init__(self):
        super().__init__(Config.STOCK_TRADES_TOPIC)

    def generate_data(self) -> dict:
        """Generate a single stock trade record."""
        from faker import Faker
        fake = Faker()
        return {
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'symbol': random.choice(Config.STOCK_SYMBOLS),
            'type': random.choice(['BUY', 'SELL']),
            'quantity': random.randint(1, 1000),
            'price': round(random.uniform(10, 500), 2)
        }

    def get_key(self, data: dict) -> str:
        """Use stock symbol as partition key for topic ordering."""
        return data['symbol']

class SocialMediaProducer(BaseProducer):
    def __init__(self):
        super().__init__(Config.SOCIAL_FEED_TOPIC)

    def generate_data(self) -> dict:
        from faker import Faker
        fake = Faker()
        hashtags = [f"#{fake.word()}" for _ in range(random.randint(0, 3))]
        return {
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'user': fake.user_name(),
            'post_id': str(fake.uuid4()),
            'content': fake.sentence(),
            'hashtags': hashtags,
            'sentiment': random.choice(Config.SENTIMENTS)
        }

    def get_key(self, data: dict) -> str:
        return data['user']

class ServerLogProducer(BaseProducer):
    def __init__(self):
        super().__init__(Config.SERVER_LOGS_TOPIC)

    def generate_data(self) -> dict:
        from faker import Faker
        fake = Faker()
        return {
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'service': random.choice(Config.SERVICES),
            'level': random.choice(Config.LEVELS),
            'message': fake.sentence(),
            'ip': fake.ipv4()
        }

    def get_key(self, data: dict) -> str:
        return data['service']