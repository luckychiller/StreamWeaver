"""
Stream consumer implementation using Strategy and Observer patterns.
Design Pattern: Strategy - Pluggable transformation algorithms per data type.
Design Pattern: Observer - Consumer reacts to Kafka messages and notifies WebSocket clients.
"""
import asyncio
import aiohttp
import time # Import the time module for sleeping in the thread
from datetime import datetime, timezone
from asyncio import Queue
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
    def transform_traffic_data(data):
        """Transform traffic data: add processing timestamp and placeholder analytics."""
        data['processed_timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
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
            topics=[Config.STOCK_TRADES_TOPIC, Config.SOCIAL_FEED_TOPIC, Config.SERVER_LOGS_TOPIC, Config.TRAFFIC_DATA_TOPIC],
            group_id='stream_consumer_group'
        )
        self.transformer = DataTransformer()
        self.publisher = WebSocketPublisher(Config.WEBSOCKET_SERVER_URL)

        # Strategy mapping: topic -> (transform_function, message_type)
        self.transform_map = {
            Config.STOCK_TRADES_TOPIC: (self.transformer.transform_stock_trade, 'stock_trade'),
            Config.SOCIAL_FEED_TOPIC: (self.transformer.transform_social_post, 'social_post'),
            Config.SERVER_LOGS_TOPIC: (self.transformer.transform_server_log, 'server_log'),
            Config.TRAFFIC_DATA_TOPIC: (self.transformer.transform_traffic_data, 'traffic_data')
        }

    def producer_loop(self, queue: Queue, loop: asyncio.AbstractEventLoop):
        """
        This is a SYNCHRONOUS function that runs in a separate thread.
        It polls Kafka and puts messages onto the asyncio queue in a thread-safe way.
        """
        while True:
            for message in self.consumer.poll_messages():
                # Use run_coroutine_threadsafe to safely schedule the async queue.put
                # operation on the main event loop.
                future = asyncio.run_coroutine_threadsafe(queue.put(message), loop)
                try:
                    # Optionally wait for the put to complete, with a timeout
                    future.result(timeout=1.0)
                except asyncio.TimeoutError:
                    print("Timeout: Failed to put message on the queue.")

            # A short sleep to prevent this thread from busy-waiting and consuming 100% CPU
            # if poll_messages returns immediately with no messages.
            time.sleep(0.01)

    async def worker(self, queue: Queue):
        """Asynchronous worker that processes messages from the queue."""
        while True:
            message = await queue.get()
            topic = message.topic
            data = message.value
            transform_func, message_type = self.transform_map.get(topic, (lambda x: x, 'unknown'))
            transformed = transform_func(data)
            await self.publisher.publish(transformed, message_type)
            print(f"Worker processed: {topic} -> {transformed}")
            queue.task_done()

    async def consume_and_process(self):
        """
        Orchestrates the producer and workers.
        """
        queue = Queue(maxsize=100) # It's good practice to have a maxsize
        loop = asyncio.get_running_loop()

        # Run the synchronous producer_loop in a separate thread pool
        producer_task = loop.run_in_executor(None, self.producer_loop, queue, loop)

        # Create asynchronous workers to process messages concurrently
        workers = [asyncio.create_task(self.worker(queue)) for _ in range(4)]

        # The application will run until one of these tasks fails.
        await asyncio.gather(producer_task, *workers)


async def main():
    consumer = StreamConsumer()
    await consumer.consume_and_process()

if __name__ == '__main__':
    asyncio.run(main())