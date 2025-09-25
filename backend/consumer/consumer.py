"""
Stream consumer implementation using Strategy and Observer patterns.
Design Pattern: Strategy - Pluggable transformation algorithms per data type.
Design Pattern: Observer - Consumer reacts to Kafka messages and notifies WebSocket clients.
"""
import asyncio
import aiohttp
from datetime import datetime, timezone
from backend.common.kafka_client import KafkaConsumerClient
from backend.common.config import Config

class DataTransformer:
    """
    Strategy pattern: Different transformation strategies for each data type.
    Each method implements a specific transformation algorithm.
    """
    @staticmethod
    def transform_stock_trade(data):
        """Transform stock trade data: add processing timestamp and placeholder analytics."""
        data['processed_timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data['moving_avg'] = data['price']  # Placeholder for moving average calculation
        return data

    @staticmethod
    def transform_social_post(data):
        """Transform social post data: add processing timestamp and hashtag analysis."""
        data['processed_timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data['hashtag_count'] = len(data['hashtags'])
        return data

    @staticmethod
    def transform_server_log(data):
        """Transform server log data: add processing timestamp and normalize level."""
        data['processed_timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data['level'] = data['level'].upper()
        return data

class WebSocketPublisher:
    """
    Publisher component for WebSocket communication.
    Handles HTTP POST to WebSocket server for broadcasting.
    """
    def __init__(self, url: str):
        self.url = url

    async def publish(self, data: dict, message_type: str):
        """Publish transformed data to WebSocket server for client broadcasting."""
        payload = {'type': message_type, 'payload': data}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.url}/publish", json=payload) as resp:
                    if resp.status != 200:
                        print(f"Failed to send to WebSocket server: {resp.status}")
            except Exception as e:
                print(f"Error sending to WebSocket server: {e}")

class StreamConsumer:
    """
    Main consumer orchestrator using Composition over Inheritance.
    Coordinates Kafka consumption, data transformation, and WebSocket publishing.
    """
    def __init__(self):
        self.consumer = KafkaConsumerClient(
            topics=[Config.STOCK_TRADES_TOPIC, Config.SOCIAL_FEED_TOPIC, Config.SERVER_LOGS_TOPIC],
            group_id='stream_consumer_group'
        )
        self.transformer = DataTransformer()
        self.publisher = WebSocketPublisher(Config.WEBSOCKET_SERVER_URL)

        # Strategy mapping: topic -> (transform_function, message_type)
        self.transform_map = {
            Config.STOCK_TRADES_TOPIC: (self.transformer.transform_stock_trade, 'stock_trade'),
            Config.SOCIAL_FEED_TOPIC: (self.transformer.transform_social_post, 'social_post'),
            Config.SERVER_LOGS_TOPIC: (self.transformer.transform_server_log, 'server_log')
        }

    async def consume_and_process(self):
        """Main processing loop: consume -> transform -> publish."""
        while True:
            for message in self.consumer.poll_messages():
                topic = message.topic
                data = message.value

                transform_func, message_type = self.transform_map.get(topic, (lambda x: x, 'unknown'))
                transformed_data = transform_func(data)

                await self.publisher.publish(transformed_data, message_type)
                print(f"Consumed and processed: {topic} -> {transformed_data}")
            await asyncio.sleep(0.1)

async def main():
    consumer = StreamConsumer()
    await consumer.consume_and_process()

if __name__ == '__main__':
    asyncio.run(main())