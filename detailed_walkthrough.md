# StreamWeaver: A Deep Dive into the Code

This document provides a highly detailed, code-level walkthrough of the entire StreamWeaver application. We will trace the execution flow file by file, explaining the purpose of each script, class, function, and variable.

## Part 1: The Producer Pipeline

The producer pipeline is responsible for generating simulated data and sending it to Kafka. We'll start with the `stock_producer` as our primary example.

### 1.1. Container Orchestration: `docker-compose.yml`

The lifecycle of our `stock_producer` begins in the [`docker-compose.yml`](docker-compose.yml) file.

```yaml
  stock_producer:
    build:
      context: .
      dockerfile: ./backend/producers/Dockerfile
    command: ["wait-for-kafka.sh", "kafka:9092", "python", "-m", "backend.producers.stock.producer"]
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
```

- **`build`**: This tells Docker Compose to build a Docker image for this service. The `context` is the root directory of the project (`.`), and the `dockerfile` is [`backend/producers/Dockerfile`](backend/producers/Dockerfile).
- **`depends_on`**: The `stock_producer` will not start until the `kafka` service is `healthy`. This health check is defined in the `kafka` service itself and ensures the broker is ready for connections.
- **`environment`**: It sets an environment variable `KAFKA_BOOTSTRAP_SERVERS` to `kafka:9092`. This is crucial for our Python application to know where to find the Kafka broker. The name `kafka` is resolvable because Docker Compose creates a private network for the services.
- **`command`**: This is the most critical part for execution flow. It specifies the command that will run when the container starts. It's a list of three parts:
    1.  `wait-for-kafka.sh`: The name of a script.
    2.  `kafka:9092`: The first argument to the script.
    3.  `python -m backend.producers.stock.producer`: The rest of the arguments, which form the command to run after the script succeeds.

### 1.2. The Producer's Environment: `backend/producers/Dockerfile`

The [`Dockerfile`](backend/producers/Dockerfile) defines the environment where the producer code will run.

- `FROM python:3.11-slim`: It starts with a lightweight Python base image.
- `WORKDIR /app`: Sets the working directory inside the container to `/app`.
- `COPY ./backend/producers/stock/requirements.txt /app/requirements.txt`: It copies the Python dependencies file into the container.
- `RUN ... pip install ...`: Installs the necessary Python packages, including `kafka-python`. It also installs Java, which is a dependency for the Kafka command-line tools.
- `RUN ... wget ... tar ...`: It downloads and extracts the official Apache Kafka binaries. This is not for running a broker, but for using the included command-line tools.
- `ENV PATH="${PATH}:/opt/kafka/bin"`: It adds the Kafka tools directory to the system's `PATH`, so we can run commands like `kafka-broker-api-versions` directly.
- `COPY ./scripts/wait-for-kafka.sh ...`: It copies the wait script into the container's path.
- `RUN chmod +x ...`: Makes the script executable.
- `COPY ./backend /app/backend`: Finally, it copies the application source code into the container.

### 1.3. The Entrypoint Script: `scripts/wait-for-kafka.sh`

This script is the first thing that runs inside the `stock_producer` container.

```bash
#!/bin/bash
set -e
host="$1"
shift
cmd="$@"

until kafka-broker-api-versions --bootstrap-server "$host" >/dev/null 2>&1; do
  >&2 echo "Kafka is unavailable - sleeping"
  sleep 5
done

>&2 echo "Kafka is up - executing command"
exec $cmd
```

1.  **`host="$1"`**: The first argument from the `docker-compose` command (`kafka:9092`) is assigned to the `host` variable.
2.  **`cmd="$@"`**: All subsequent arguments (`python -m backend.producers.stock.producer`) are concatenated and assigned to the `cmd` variable.
3.  **`until ...`**: This is a loop. It executes the command `kafka-broker-api-versions --bootstrap-server "$host"`.
    - `kafka-broker-api-versions` is a command-line tool from the Kafka binaries we installed. It's a simple way to check if a connection to the broker can be established.
    - `>/dev/null 2>&1` redirects all output (standard and error) to `/dev/null`, so we don't see the command's output, we only care about its success or failure.
    - If the command fails (because Kafka isn't ready yet), the loop prints "Kafka is unavailable - sleeping", waits for 5 seconds, and tries again.
4.  **`exec $cmd`**: Once the `until` loop exits (meaning the Kafka broker responded successfully), this line is executed. `exec` replaces the current process (the script) with the command stored in the `cmd` variable. The container is now running our Python application.

### 1.4. Application Configuration: `backend/common/config.py`

Before diving into the producer logic, let's look at how it's configured.

```python
import os

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    # ... other configs
    STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    STOCK_TRADES_TOPIC = 'stock_trades'
```

- **`Config` Class**: This class acts as a centralized place for all configuration settings.
- **`KAFKA_BOOTSTRAP_SERVERS`**: This is a class variable. `os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')` reads the value of the environment variable `KAFKA_BOOTSTRAP_SERVERS`.
    - Inside our Docker container, this environment variable was set to `kafka:9092` by Docker Compose. So, `Config.KAFKA_BOOTSTRAP_SERVERS` will hold the string `'kafka:9092'`.
    - The `'localhost:9092'` is a default value used only if the environment variable is not set (e.g., when running locally outside of Docker).
- **`STOCK_SYMBOLS`**: A list of strings that the stock producer will use to generate data.
- **`STOCK_TRADES_TOPIC`**: A string variable holding the name of the Kafka topic (`'stock_trades'`) where the data will be sent.

### 1.5. The Kafka Client Wrapper: `backend/common/kafka_client.py`

This file provides a simplified interface for interacting with Kafka.

```python
from kafka import KafkaProducer
import json
from .config import Config

class KafkaProducerClient:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def send_message(self, topic: str, message: dict, key: str = None):
        self.producer.send(topic, value=message, key=key)
        self.producer.flush()
```

- **`KafkaProducerClient` Class**: A wrapper around the `kafka-python` library's `KafkaProducer`.
- **`__init__(self)`**: The constructor is called when a new `KafkaProducerClient` object is created.
    1.  **`self.producer = KafkaProducer(...)`**: It creates an instance of the underlying `KafkaProducer`.
    2.  **`bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS`**: This is the most important parameter. It tells the producer where to connect. As we saw, this value is `'kafka:9092'`.
    3.  **`value_serializer`**: This parameter requires a function that defines how message values are converted to bytes before being sent over the network. The `lambda v: json.dumps(v).encode('utf-8')` function does two things:
        - `json.dumps(v)`: Takes a Python dictionary (`v`) and converts it into a JSON formatted string.
        - `.encode('utf-8')`: Takes the JSON string and encodes it into a sequence of bytes using the UTF-8 standard.
- **`send_message(...)`**: This method simplifies the process of sending a message.
    1.  **`self.producer.send(topic, value=message, key=key)`**: It calls the underlying producer's `send` method, passing the topic name and the message dictionary. The `value_serializer` we defined earlier is automatically called on the `message` dictionary.
    2.  **`self.producer.flush()`**: This method forces all buffered messages to be sent to the Kafka broker immediately. It's a blocking call that waits for the broker to acknowledge receipt of the message. This ensures that when our function returns, the message is guaranteed to be in Kafka.

### 1.6. The Producer's Entry Point: `backend/producers/stock/producer.py`

This is the main script for the stock producer, executed by the `python -m` command.

```python
import asyncio
from backend.producers.base.producer import StockTradeProducer

async def main():
    producer = StockTradeProducer()
    await producer.produce(interval=0.01)

if __name__ == '__main__':
    asyncio.run(main())
```

- **`if __name__ == '__main__':`**: This is the standard entry point for a Python script. When the file is run directly, this block is executed.
- **`asyncio.run(main())`**: This starts the `asyncio` event loop and runs the `main` asynchronous function until it completes.
- **`async def main():`**: The main logic of our script.
    1.  **`producer = StockTradeProducer()`**: An object of the `StockTradeProducer` class is created. We will examine this class next.
    2.  **`await producer.produce(interval=0.01)`**: It calls the `produce` method on the newly created object. The `await` keyword pauses the execution of `main` until the `produce` method completes. The `interval=0.01` argument tells the producer to generate a message every 0.01 seconds.

This is the end of Part 1. In the next part, we will dive into the `StockTradeProducer` base class to see how the data is actually generated, and then trace the flow through the consumer to the frontend.
## Part 2: Data Generation and Abstraction

Now, we'll explore the heart of the data generation logic, which resides in the [`backend/producers/base/producer.py`](backend/producers/base/producer.py) file. This file uses object-oriented principles to create a reusable and extensible system for producing different kinds of data.

### 2.1. The Abstract Base Class: `BaseProducer`

This class serves as a template for all specific producers. It uses a design pattern called the **Template Method**. The idea is to define the skeleton of an algorithm in a base class, but let subclasses override specific steps of the algorithm without changing its structure.

```python
from abc import ABC, abstractmethod
import asyncio
import random
from ...common.kafka_client import KafkaProducerClient

class BaseProducer(ABC):
    def __init__(self, topic: str):
        self.topic = topic
        self.kafka_producer = KafkaProducerClient()

    @abstractmethod
    def generate_data(self) -> dict:
        pass

    async def produce(self, interval: float = 0.1):
        while True:
            data = self.generate_data()
            key = self.get_key(data)
            self.kafka_producer.send_message(self.topic, data, key)
            print(f"Produced to {self.topic}: {data}")
            await asyncio.sleep(random.uniform(interval * 0.5, interval * 1.5))

    def get_key(self, data: dict) -> str:
        return None
```

- **`class BaseProducer(ABC)`**: It inherits from `ABC` (Abstract Base Class), which means it cannot be instantiated on its own. It's meant to be subclassed.
- **`__init__(self, topic: str)`**: The constructor.
    - `self.topic = topic`: Stores the name of the Kafka topic that this producer will send messages to.
    - `self.kafka_producer = KafkaProducerClient()`: This is a crucial step. It creates an instance of our `KafkaProducerClient` wrapper. This single object will be used for the entire lifetime of the producer to send messages. A new connection to Kafka is established here.
- **`@abstractmethod def generate_data(self) -> dict`**: This defines an abstract method. It declares that any class that inherits from `BaseProducer` *must* implement its own version of the `generate_data` method. This is the part of the algorithm that subclasses will define.
- **`async def produce(self, interval: float = 0.1)`**: This is the **template method**. It defines the fixed algorithm for producing data.
    1.  `while True:`: An infinite loop to continuously generate data.
    2.  `data = self.generate_data()`: It calls the `generate_data` method. Because of polymorphism, Python will call the implementation of this method from the *subclass* (e.g., `StockTradeProducer`), not the base class.
    3.  `key = self.get_key(data)`: It calls the `get_key` method to get a partitioning key for the message.
    4.  `self.kafka_producer.send_message(self.topic, data, key)`: It uses the `kafka_producer` object to send the generated `data` to the `self.topic`.
    5.  `await asyncio.sleep(...)`: It pauses the loop asynchronously for a short duration. The `random.uniform` adds a bit of "jitter" to the interval, so messages aren't produced in a perfectly rigid rhythm, simulating a more realistic data flow.
- **`def get_key(self, data: dict) -> str`**: This is a "hook" method. It provides a default implementation (returning `None`, which means Kafka will use round-robin partitioning). Subclasses can optionally override this method to provide a specific key for partitioning. Messages with the same key are guaranteed to go to the same partition, which is important for ensuring order for related messages.

### 2.2. The Concrete Implementation: `StockTradeProducer`

This is the class that we actually instantiate in our main script. It inherits from `BaseProducer` and provides the missing pieces.

```python
from ...common.config import Config
from datetime import datetime, timezone
import random

class StockTradeProducer(BaseProducer):
    def __init__(self):
        super().__init__(Config.STOCK_TRADES_TOPIC)

    def generate_data(self) -> dict:
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
        return data['symbol']
```

- **`__init__(self)`**: The constructor for the `StockTradeProducer`.
    - **`super().__init__(Config.STOCK_TRADES_TOPIC)`**: This is a critical line. It calls the constructor of the parent class (`BaseProducer`). It passes `Config.STOCK_TRADES_TOPIC` (the string `'stock_trades'`) as the `topic`. This is how the `BaseProducer` knows which topic to send messages to.
- **`generate_data(self) -> dict`**: This is the required implementation of the abstract method. This method is called repeatedly by the `produce` loop in the `BaseProducer`.
    1.  `from faker import Faker`: It imports the `Faker` library, which is used to generate realistic-looking fake data. The import is done inside the method to avoid loading it if the producer is never used, a minor optimization.
    2.  `fake = Faker()`: Creates an instance of the `Faker` data generator.
    3.  **`return {...}`**: It constructs and returns a Python dictionary. This is a single "message".
        - `'timestamp'`: A new variable is created. `datetime.now(timezone.utc)` gets the current time in UTC. `.strftime(...)` formats it into a standard ISO 8601 string.
        - `'symbol'`: A new variable is created. `random.choice(Config.STOCK_SYMBOLS)` selects a random stock symbol (e.g., 'AAPL') from the list we defined in `config.py`.
        - `'type'`, `'quantity'`, `'price'`: These variables are created using the `random` library to generate plausible trade data.
- **`get_key(self, data: dict) -> str`**: This overrides the default `get_key` method.
    - **`return data['symbol']`**: It returns the stock symbol from the data dictionary. For example, if the generated data is for 'AAPL', this method returns 'AAPL'. This means all trades for 'AAPL' will be sent to the same Kafka partition, ensuring that they are processed in the order they were produced. The same logic applies to 'GOOGL', 'MSFT', etc.

**Summary of the Flow:**

1.  `stock/producer.py` creates a `StockTradeProducer` object.
2.  The `StockTradeProducer` constructor calls the `BaseProducer` constructor, setting the topic to `'stock_trades'` and creating a `KafkaProducerClient`.
3.  `stock/producer.py` calls the `produce()` method (defined in `BaseProducer`).
4.  The `produce()` method's loop calls `generate_data()` (defined in `StockTradeProducer`), which creates a new dictionary of trade data.
5.  The `produce()` method's loop calls `get_key()` (defined in `StockTradeProducer`) to get the stock symbol as the partition key.
6.  The `produce()` method's loop calls `send_message()` on the `kafka_producer` object, sending the data and key to Kafka.
7.  The loop sleeps and repeats.

The `SocialMediaProducer` and `ServerLogProducer` classes follow the exact same pattern, but provide different implementations for `generate_data` and `get_key` to produce their respective data types.

The next part will trace the journey of the message from the Kafka broker to the consumer.
## Part 3: The Consumer and WebSocket Pipeline

This part of the pipeline is responsible for reading messages from Kafka, applying a simple transformation, and then pushing them to the frontend via a WebSocket server.

### 3.1. Container Orchestration: `docker-compose.yml`

Let's look at the relevant services in the [`docker-compose.yml`](docker-compose.yml) file.

```yaml
  stream_consumer:
    build:
      context: .
      dockerfile: ./backend/consumer/Dockerfile
    command: ["wait-for-kafka.sh", "kafka:9092", "python", "-m", "backend.consumer.consumer"]
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      WEBSOCKET_SERVER_URL: http://websocket_server:8080

  websocket_server:
    build: ./backend/websocket
    depends_on:
      - stream_consumer
    ports:
      - "8080:8080"
```

- **`stream_consumer` service**:
    - **`build` & `command`**: Similar to the producers, it builds from a [`Dockerfile`](backend/consumer/Dockerfile) and uses the `wait-for-kafka.sh` script to ensure Kafka is ready before executing the main Python script [`backend/consumer/consumer.py`](backend/consumer/consumer.py).
    - **`environment`**: It sets two important environment variables:
        - `KAFKA_BOOTSTRAP_SERVERS`: Tells the consumer where to find Kafka (`kafka:9092`).
        - `WEBSOCKET_SERVER_URL`: Provides the address of the WebSocket server (`http://websocket_server:8080`).
- **`websocket_server` service**:
    - **`build`**: It builds an image from the [`backend/websocket`](backend/websocket) directory, which has its own `Dockerfile`.
    - **`depends_on`**: It waits for the `stream_consumer` to start. This isn't strictly necessary for operation, but it establishes a logical startup order.
    - **`ports`**: It maps port `8080` of the container to port `8080` on the host machine, so you could an access it from your browser for debugging if needed.

### 3.2. The Consumer's Environment: `backend/consumer/Dockerfile`

The [`Dockerfile`](backend/consumer/Dockerfile) for the consumer is very similar to the producer's, setting up Python, installing dependencies from `requirements.txt`, and copying the source code.

### 3.3. The Kafka Client Wrapper (Consumer): `backend/common/kafka_client.py`

We now look at the other class in our Kafka client file.

```python
from kafka import KafkaConsumer
import json
from .config import Config

class KafkaConsumerClient:
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
        return self.consumer
```

- **`__init__(self, topics: list, group_id: str)`**: The constructor.
    1.  `self.consumer = KafkaConsumer(...)`: Creates an instance of the `KafkaConsumer` from the `kafka-python` library.
    2.  `*topics`: The `*` unpacks the list of topic names (e.g., `['stock_trades', 'social_feed']`) into separate arguments for the function.
    3.  `bootstrap_servers`: Connects to Kafka at `kafka:9092`.
    4.  `group_id`: This is a very important concept in Kafka. All consumers with the same `group_id` are part of a single consumer group. Kafka ensures that each message in the topics is delivered to only *one* consumer instance within that group. This is how you can scale up consumption by running multiple instances of the same service.
    5.  `auto_offset_reset='latest'`: If this consumer is new (or has been down for a long time), this tells it to start reading messages from the very end of the topic (i.e., only new messages that arrive after it starts).
    6.  `value_deserializer`: This is the reverse of the producer's serializer. The `lambda x: json.loads(x.decode('utf-8'))` function takes a sequence of bytes (`x`), `decode`s it from UTF-8 into a JSON string, and then `json.loads` parses that string back into a Python dictionary.
- **`poll_messages(self)`**: This method simply returns the underlying `consumer` object, which can be iterated over to get messages.

### 3.4. The Main Consumer Logic: `backend/consumer/consumer.py`

This file orchestrates the process of consuming, transforming, and forwarding the data. It uses the **Strategy** design pattern to handle different types of data.

```python
import asyncio
import aiohttp
from backend.common.kafka_client import KafkaConsumerClient
from backend.common.config import Config

class DataTransformer:
    # ... (static methods for transformation)

class WebSocketPublisher:
    # ... (publish method)

class StreamConsumer:
    def __init__(self):
        self.consumer = KafkaConsumerClient(
            topics=[Config.STOCK_TRADES_TOPIC, Config.SOCIAL_FEED_TOPIC, Config.SERVER_LOGS_TOPIC],
            group_id='stream_consumer_group'
        )
        self.transformer = DataTransformer()
        self.publisher = WebSocketPublisher(Config.WEBSOCKET_SERVER_URL)
        self.transform_map = {
            Config.STOCK_TRADES_TOPIC: (self.transformer.transform_stock_trade, 'stock_trade'),
            # ... other topics
        }

    async def consume_and_process(self):
        while True:
            for message in self.consumer.poll_messages():
                topic = message.topic
                data = message.value
                transform_func, message_type = self.transform_map.get(topic, (lambda x: x, 'unknown'))
                transformed_data = transform_func(data)
                await self.publisher.publish(transformed_data, message_type)
            await asyncio.sleep(0.1)

# ... (main entry point)
```

- **`StreamConsumer.__init__`**:
    1.  `self.consumer = KafkaConsumerClient(...)`: Creates a consumer client instance, subscribing to all three topics and joining the `stream_consumer_group`.
    2.  `self.transformer = DataTransformer()`: Creates an instance of the `DataTransformer` class, which contains our transformation logic.
    3.  `self.publisher = WebSocketPublisher(...)`: Creates a publisher instance, pointing it to the WebSocket server's URL.
    4.  `self.transform_map`: This dictionary is the core of the **Strategy** pattern. It maps a topic name (the key) to a tuple containing the specific transformation function to use and a simple string identifier for that data type.
- **`StreamConsumer.consume_and_process`**:
    1.  `while True:`: An infinite loop to continuously process messages.
    2.  `for message in self.consumer.poll_messages():`: The `kafka-python` consumer is iterable. This loop will block until one or more messages are available from Kafka, and then it will iterate through them.
    3.  `topic = message.topic`: A new variable `topic` is created to hold the topic name the message came from (e.g., `'stock_trades'`).
    4.  `data = message.value`: A new variable `data` is created. This holds the Python dictionary that has been automatically deserialized by our `value_deserializer`.
    5.  `transform_func, message_type = self.transform_map.get(topic, ...)`: This looks up the `topic` in our `transform_map`. It retrieves the correct transformation function (`transform_stock_trade`) and the message type string (`'stock_trade'`).
    6.  `transformed_data = transform_func(data)`: It calls the retrieved function, passing the `data`. The function adds a `processed_timestamp` and a `moving_avg` placeholder, and returns the modified dictionary, which is stored in the new `transformed_data` variable.
    7.  `await self.publisher.publish(transformed_data, message_type)`: It calls the `publish` method, which sends the final data to the WebSocket server.

- **`WebSocketPublisher.publish`**:

```python
class WebSocketPublisher:
    async def publish(self, data: dict, message_type: str):
        payload = {'type': message_type, 'payload': data}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.url}/publish", json=payload) as resp:
                    # ... error handling
```

1.  `payload = {'type': message_type, 'payload': data}`: It wraps our data in another dictionary. This is a common pattern to provide metadata to the frontend, so it knows what kind of data it's receiving. The final payload looks like: `{'type': 'stock_trade', 'payload': {'symbol': 'AAPL', ...}}`.
2.  `session.post(f"{self.url}/publish", json=payload)`: It uses the `aiohttp` library to make an asynchronous HTTP POST request to the `/publish` endpoint on our WebSocket server. The `json=payload` argument automatically serializes the Python dictionary to a JSON request body.

### 3.5. The WebSocket Server: `backend/websocket/server.py`

This server acts as a bridge, receiving data via HTTP and broadcasting it to all connected frontend clients via WebSockets.

```python
from aiohttp import web
import json
import asyncio

connected_clients = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.add(ws)
    # ... (handles client connection lifecycle)

async def publish_handler(request):
    data = await request.json()
    message = json.dumps(data)
    if connected_clients:
        await asyncio.gather(*[client.send_str(message) for client in connected_clients])
    return web.Response(text="OK")

async def init_app():
    app = web.Application()
    app.router.add_get('/ws/data', websocket_handler)
    app.router.add_post('/publish', publish_handler)
    return app
```

- **`connected_clients = set()`**: A global `set` used to keep track of all active WebSocket connections. A `set` is used because it automatically handles adding/removing items and prevents duplicates.
- **`init_app()`**: This function sets up the server's routes.
    - `/ws/data`: The GET endpoint that a client connects to to initiate a WebSocket connection. The `websocket_handler` manages this.
    - `/publish`: The POST endpoint that our `StreamConsumer` sends data to. The `publish_handler` manages this.
- **`websocket_handler`**: When a frontend client connects, this handler adds the new WebSocket connection object (`ws`) to the `connected_clients` set. It then waits for the client to disconnect, at which point it removes the connection from the set.
- **`publish_handler`**:
    1.  `data = await request.json()`: It receives the HTTP POST request and deserializes the JSON body back into a Python dictionary (`data`). This is the payload we sent from the consumer: `{'type': 'stock_trade', ...}`.
    2.  `message = json.dumps(data)`: It re-serializes the dictionary back into a JSON string, which is stored in the `message` variable.
    3.  `await asyncio.gather(*[client.send_str(message) for client in connected_clients])`: This is the broadcast mechanism. It iterates through every client connection in the `connected_clients` set and sends them the same JSON `message` string. `asyncio.gather` runs all the send operations concurrently.

The final part of this walkthrough will cover the frontend code, showing how it connects to the WebSocket and displays the data.
## Part 4: The Frontend - Real-time Visualization

The final piece of the puzzle is the frontend application, which receives the data pushed by the WebSocket server and renders it in real-time. This is a React application built with TypeScript and Vite.

### 4.1. Container Orchestration & Build: `docker-compose.yml` and `Dockerfile`

```yaml
# docker-compose.yml
  web_dashboard:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - websocket_server
```

- **`build`**: Docker Compose is instructed to build the frontend using the [`frontend`](frontend) directory.
- **`ports`**: It maps port `80` inside the container to port `3000` on the host machine. This means you can access the dashboard by navigating to `http://localhost:3000` in your browser.

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

This is a **multi-stage Dockerfile** which is a best practice for building web frontends.

- **Stage 1 (`build`)**:
    1.  `FROM node:18-alpine`: Starts with a Node.js image to get access to `npm`.
    2.  `RUN npm install`: Installs all the development dependencies needed to build the React project.
    3.  `COPY . .`: Copies the entire frontend source code.
    4.  `RUN npm run build`: This command (defined in [`package.json`](frontend/package.json)) triggers Vite to compile the TypeScript/React code into a set of optimized, static HTML, CSS, and JavaScript files, placing them in the `/app/dist` directory.
- **Stage 2 (Final Image)**:
    1.  `FROM nginx:alpine`: Starts with a very lightweight Nginx web server image.
    2.  `COPY --from=build /app/dist ...`: This is the key step. It copies *only* the static files from the `dist` directory of the `build` stage into the Nginx server's public directory. The Node.js environment and all the source code are discarded, resulting in a tiny, secure, and efficient final image.
    3.  `CMD ["nginx", "-g", "daemon off;"]`: The default command to start the Nginx server.

### 4.2. Establishing the WebSocket Connection: `useWebSocket.ts`

This is a custom React hook that encapsulates all the logic for managing the WebSocket connection. A custom hook is a reusable function that lets you share stateful logic between components.

```typescript
// frontend/hooks/useWebSocket.ts
import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url: string, onMessage: (message: WebSocketMessage) => void): WebSocketStatus => {
  const [status, setStatus] = useState<WebSocketStatus>(WebSocketStatus.CONNECTING);
  const ws = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    setStatus(WebSocketStatus.CONNECTING);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setStatus(WebSocketStatus.CONNECTED);
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };

    ws.current.onclose = () => {
      // ... logic to attempt reconnection
    };
  }, [url, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  return status;
};
```

- **`useWebSocket` Function**: It takes a `url` and a callback function `onMessage` as arguments.
- **`status` State**: A new state variable `status` is created to track the connection status (e.g., 'CONNECTING', 'CONNECTED').
- **`ws` Ref**: A `useRef` is used to hold the WebSocket object. A ref is like a "box" that can hold a mutable value. Unlike state, changing a ref does not trigger a re-render. This is perfect for storing things like the WebSocket instance.
- **`connect` Function**: This function contains the core logic.
    1.  `ws.current = new WebSocket(url)`: This is the native browser API that opens a new WebSocket connection to the specified `url`. In our app, the URL will be `ws://localhost:8080/ws/data`.
    2.  `ws.current.onopen = () => ...`: This assigns a callback function to the `onopen` event. It fires when the connection is successfully established, and we update our `status` state.
    3.  `ws.current.onmessage = (event) => ...`: This assigns a callback to the `onmessage` event. This function is the heart of our real-time updates. It fires **every time the server sends a message**.
        - `event.data`: This variable contains the raw message from the server, which is the JSON string we broadcasted.
        - `const message = JSON.parse(event.data)`: A new `message` variable is created by parsing the JSON string into a JavaScript object.
        - `onMessage(message)`: It calls the callback function that was passed into the hook, handing it the parsed message object.
- **`useEffect` Hook**:
    - `connect()`: This hook runs once when the component that uses it first mounts. It calls the `connect` function to initiate the connection.
    - `return () => ...`: The function returned from `useEffect` is a cleanup function. It runs when the component unmounts, ensuring the WebSocket connection is properly closed to prevent memory leaks.

### 4.3. The Main Application Component: `App.tsx`

This is the root component of our application. It orchestrates the state and passes data down to the display components.

```typescript
// frontend/App.tsx
import React, { useState, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import StockTradesPanel from './components/StockTradesPanel';
import { WEBSOCKET_URL } from './constants';

const App: React.FC = () => {
  const [stockTrades, setStockTrades] = useState<StockTradePayload[]>([]);
  // ... state for other data types

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'stock_trade':
        setStockTrades(prev => [message.payload, ...prev].slice(0, MAX_STOCK_TRADES));
        break;
      // ... cases for other message types
    }
  }, []);

  const connectionStatus = useWebSocket(WEBSOCKET_URL, handleWebSocketMessage);

  return (
    <div>
      <Header status={connectionStatus} />
      <main>
        {/* ... other components */}
        <StockTradesPanel trades={stockTrades} />
        {/* ... other components */}
      </main>
    </div>
  );
};
```
- **State Management**:
    - `const [stockTrades, setStockTrades] = useState<StockTradePayload[]>([])`: This creates a state variable named `stockTrades`. It is an array that will hold the incoming stock trade messages. `setStockTrades` is the function used to update this state.
- **`handleWebSocketMessage`**:
    - This function is defined using `useCallback` for performance optimization. It will be passed as the `onMessage` callback to our `useWebSocket` hook.
    - `switch (message.type)`: It checks the `type` property of the incoming message object (e.g., `'stock_trade'`). This is the type we set in the consumer.
    - `setStockTrades(prev => [message.payload, ...prev].slice(0, MAX_STOCK_TRADES))`: This is the state update logic.
        - `setStockTrades` is called with a function that receives the *previous* state (`prev`).
        - `[message.payload, ...prev]`: A new array is created. It takes the new trade payload from the message and places it at the beginning, followed by all the elements of the previous array.
        - `.slice(0, MAX_STOCK_TRADES)`: This keeps the array from growing indefinitely by truncating it to a maximum size.
    - When `setStockTrades` is called, React knows that the component's state has changed and triggers a re-render of the `App` component and any of its children that depend on the `stockTrades` state.
- **Hook Usage**:
    - `const connectionStatus = useWebSocket(WEBSOCKET_URL, handleWebSocketMessage)`: This line is where we use our custom hook. It initiates the connection and registers our `handleWebSocketMessage` function to be called for every message. The hook returns the current `connectionStatus`, which we can use in the UI.
- **Rendering**:
    - `<StockTradesPanel trades={stockTrades} />`: The `App` component renders the `StockTradesPanel` component. It passes the `stockTrades` array as a prop. Whenever the `stockTrades` state changes, this component will receive the new array and re-render itself to display the latest data.

### 4.4. The Display Component: `StockTradesPanel.tsx`

This component is responsible for visualizing the stock trade data.

```typescript
// frontend/components/StockTradesPanel.tsx
import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

const StockTradesPanel: React.FC<StockTradesPanelProps> = ({ trades }) => {
  const chartData = useMemo(() => {
    // ... logic to transform the trades array for the chart
  }, [trades]);

  const recentTrades = useMemo(() => trades.slice(0, 8), [trades]);

  return (
    <Card>
      <BarChart data={chartData}>
        {/* ... chart configuration */}
      </BarChart>
      <div>
        {recentTrades.map(trade => (
          // ... render a row for each recent trade
        ))}
      </div>
    </Card>
  );
};
```
- **Props**: It receives the `trades` array as a prop from the `App` component.
- **`useMemo`**: This hook is used for performance optimization. It memoizes the result of a calculation.
    - The code inside `useMemo` is only re-executed if its dependency (`[trades]`) changes.
    - `chartData`: A variable `chartData` is created by transforming the raw `trades` array into a format suitable for the `recharts` library.
    - `recentTrades`: A variable `recentTrades` is created containing just the first 8 trades to display in a list.
- **Rendering**:
    - The component uses the `recharts` library to render a `<BarChart>` using the `chartData`.
    - It also maps over the `recentTrades` array to render a list of the most recent individual trades.

This concludes the deep dive into the StreamWeaver application. We have traced the full journey of a message: from its creation in a Python producer script, through a Kafka topic, into a consumer that transforms it, getting pushed to a WebSocket server, and finally being rendered in real-time on a React frontend.