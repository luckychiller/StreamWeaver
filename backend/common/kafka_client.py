"""
Kafka client wrappers using Facade pattern to simplify Kafka operations.
Design Pattern: Facade - Provides a simplified interface to complex Kafka operations.
"""
from abc import ABC, abstractmethod
from kafka import KafkaProducer, KafkaConsumer
import json
from .config import Config

class KafkaProducerClient:
    """
    Wrapper for Kafka producer operations.
    Handles serialization and connection management.
    """
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def send_message(self, topic: str, message: dict, key: str = None):
        """Send a message to the specified Kafka topic."""
        self.producer.send(topic, value=message, key=key)

class KafkaConsumerClient:
    """
    Wrapper for Kafka consumer operations.
    Manages consumer groups and deserialization.
    """
    def __init__(self, topics: list, group_id: str):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def poll_messages(self):
        """Return the underlying consumer for message polling."""
        return self.consumer