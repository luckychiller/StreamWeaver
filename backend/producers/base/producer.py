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
        """Hook method: Can be overridden for custom partitioning keys."""
        return None

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
    

class TrafficProducer(BaseProducer):
    """
    Concrete implementation for traffic data production.
    Generates realistic stock trading data with timestamps and market symbols.
    """
    def __init__(self):
        super().__init__(Config.TRAFFIC_DATA_TOPIC)

    def _generate_weather_condition(self, timestamp: datetime) -> tuple[str, float, float]:
        """Generate realistic weather conditions."""
        # Simple weather simulation - in reality this would use weather APIs
        month = timestamp.month

        # Winter months (Dec-Feb) - higher chance of snow/cold
        if month in [12, 1, 2]:
            weather_roll = random.random()
            if weather_roll < 0.3:
                return "snow", random.uniform(0.1, 8.0), 0.0
            elif weather_roll < 0.5:
                return "extreme_cold", 10.0, 0.0
            elif weather_roll < 0.7:
                return "cloudy", random.uniform(5.0, 10.0), 0.0
            else:
                return "clear", 10.0, 0.0

        # Summer months (Jun-Aug) - higher chance of heat/rain
        elif month in [6, 7, 8]:
            weather_roll = random.random()
            if weather_roll < 0.2:
                return "extreme_heat", random.uniform(0.1, 5.0), 0.0
            elif weather_roll < 0.4:
                return "heavy_rain", 10.0, random.uniform(0.5, 2.0)
            elif weather_roll < 0.6:
                return "light_rain", 10.0, random.uniform(0.1, 0.4)
            else:
                return "clear", 10.0, 0.0

        # Other months - moderate weather
        else:
            weather_roll = random.random()
            if weather_roll < 0.1:
                return "light_rain", 10.0, random.uniform(0.1, 0.3)
            elif weather_roll < 0.2:
                return "fog", random.uniform(0.5, 2.0), 0.0
            else:
                return "clear", 10.0, 0.0

    def generate_data(self) -> dict:
        """Generate a single traffic data record."""        
        timestamp = datetime.utcnow()
        # Generate weather conditions
        weather_condition, visibility, precipitation = self._generate_weather_condition(timestamp)

        return {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "location_id":random.choice(Config.TRAFFIC_LOCATION),
            "vehicle_count":random.randint(0,100),
            "average_speed":random.uniform(1, 100) ,
            "congestion_level":random.choice(Config.CONGESTION_LEVEL),
            "direction":random.choice(Config.TRAFFIC_DIRECTION),
            "occupancy_rate":random.randint(0,100),
            "headway_seconds":random.randint(0,100),
            "weather_condition":weather_condition,
            "visibility_miles":visibility,
            "precipitation_inches":precipitation
        }

    def get_key(self, data: dict) -> str:
        """Use location_id as partition key for topic ordering."""
        return data['location_id']