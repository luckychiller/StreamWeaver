# StreamWeaver: From `docker-compose up` to Live Data

This document provides a detailed, step-by-step walkthrough of the entire StreamWeaver application lifecycle, starting from the moment you run `docker-compose up` to the point where live data appears on the web dashboard.

## 1. Initializing the System: `docker-compose up`

When you execute `docker-compose up -d`, Docker Compose reads the [`docker-compose.yml`](docker-compose.yml) file and begins orchestrating a multi-container application. It builds and starts services in an order determined by the `depends_on` directives.

### Step 1.1: Zookeeper Starts

- **Service**: `zookeeper`
- **Action**: Docker pulls the `confluentinc/cp-zookeeper:7.4.0` image. A container named `zookeeper` is created and started.
- **Role**: Zookeeper is the first service to start. It acts as a centralized coordination service. In our Kafka setup, its primary job is to manage the metadata of the Kafka cluster, such as tracking which brokers are alive, storing topic configurations, and managing consumer group offsets. It is the source of truth for the cluster's state.

### Step 1.2: Kafka Broker Starts

- **Service**: `kafka`
- **Action**: Because `kafka` `depends_on` `zookeeper`, Docker Compose waits for the Zookeeper container to be running before starting this one. It pulls the `confluentinc/cp-kafka:7.4.0` image and starts the container.
- **Configuration & Role**:
    - The Kafka broker starts and immediately connects to Zookeeper (`KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181`). It registers itself with Zookeeper as an active broker.
    - Upon successful startup, it an in-built startup script specified via the `KAFKA_CREATE_TOPICS` environment variable. This command creates three topics: `stock_trades`, `social_feed`, and `server_logs`. Each topic is created with 1 partition and a replication factor of 1.
- **Health Check**: The `healthcheck` configured for the `kafka` service begins running. It periodically executes `kafka-topics --bootstrap-server kafka:9092 --list` inside the container. This command succeeds only when the Kafka broker is fully operational and ready to accept connections. Other services will wait for this health check to pass before they start.

### Step 1.3: Data Producers Initialize

- **Services**: `stock_producer`, `social_producer`, `log_producer`
- **Action**: These services `depend_on` `kafka` with `condition: service_healthy`. Docker Compose waits for the Kafka health check (from step 1.2) to pass.
- **Build & Command**:
    - For each producer, Docker builds an image using the [`backend/producers/Dockerfile`](backend/producers/Dockerfile).
    - The `command` for each producer is `["wait-for-kafka.sh", "kafka:9092", "python", "-m", "backend.producers.stock.producer"]` (and similarly for the others).
    - The [`scripts/wait-for-kafka.sh`](scripts/wait-for-kafka.sh) script runs first. It's a small utility that waits until it can successfully establish a connection with the Kafka broker at `kafka:9092` before proceeding.
    - Once the connection is confirmed, the script executes the Python producer module (e.g., `python -m backend.producers.stock.producer`).

### Step 1.4: The Consumer and WebSocket Server Start

- **Service**: `stream_consumer`
- **Action**: This service also waits for Kafka's health check to pass.
- **Mechanism**:
    - It is built from [`backend/consumer/Dockerfile`](backend/consumer/Dockerfile).
    - The [`wait-for-kafka.sh`](scripts/wait-for-kafka.sh) script ensures Kafka is ready.
    - The Python script [`backend/consumer/consumer.py`](backend/consumer/consumer.py) is executed. Its first action is to create a `KafkaConsumerClient` which subscribes to all three topics: `stock_trades`, `social_feed`, and `server_logs`. It joins a consumer group and is now ready to receive messages.

- **Service**: `websocket_server`
- **Action**: This service `depends_on` `stream_consumer`. It is built from [`backend/websocket/Dockerfile`](backend/websocket/Dockerfile).
- **Mechanism**:
    - Once the `stream_consumer` container is running, the `websocket_server` starts.
    - The Python script [`backend/websocket/server.py`](backend/websocket/server.py) runs, opening a WebSocket server that listens for incoming connections on port `8080`.

### Step 1.5: The Frontend Dashboard Starts

- **Service**: `web_dashboard`
- **Action**: This service `depends_on` `websocket_server`.
- **Mechanism**:
    - It is built from [`frontend/Dockerfile`](frontend/Dockerfile), which compiles the React application into static files and serves them with a web server.
    - The container starts and exposes the web dashboard on port `3000`. At this point, all services are running, and the system is live.

## 2. The Journey of a Single Message

Let's trace a single "stock trade" message from creation to display.

### Step 2.1: Data Generation (Producer)

- **Service**: `stock_producer`
- **Action**: The running script in [`backend/producers/stock/producer.py`](backend/producers/stock/producer.py) enters a loop.
- **Mechanism**:
    - Inside the loop, it generates a Python dictionary representing a fake stock trade (e.g., `{'timestamp': '...', 'symbol': 'AAPL', 'price': 150.00, ...}`).
    - It uses the `KafkaProducerClient` from [`backend/common/kafka_client.py`](backend/common/kafka_client.py) to send this message.
    - The client serializes the dictionary into a JSON string, encodes it to UTF-8 bytes, and sends it to the `stock_trades` topic on the Kafka broker at `kafka:9092`. The producer then waits for a short interval before generating the next message.

### Step 2.2: Message Queuing (Kafka)

- **Service**: `kafka`
- **Action**: The Kafka broker receives the message from the `stock_producer`.
- **Mechanism**:
    - It appends the message to the end of the log for the `stock_trades` topic.
    - The message is now durably stored on the broker's disk. It is immediately available to be read by any consumer subscribed to this topic.

### Step 2.3: Data Consumption and Forwarding (Consumer)

- **Service**: `stream_consumer`
- **Action**: The `KafkaConsumerClient` in [`backend/consumer/consumer.py`](backend/consumer/consumer.py) is constantly polling Kafka for new messages.
- **Mechanism**:
    - The consumer "wakes up," and its poll request fetches the new stock trade message from the `stock_trades` topic.
    - The client deserializes the message from UTF-8 bytes back into a JSON string, and then into a Python dictionary.
    - The consumer script then makes an HTTP POST request, sending this dictionary as a JSON payload to the WebSocket server at `http://websocket_server:8080`. This URL is configured via the `WEBSOCKET_SERVER_URL` environment variable.

### Step 2.4: Real-time Broadcasting (WebSocket Server)

- **Service**: `websocket_server`
- **Action**: The server at [`backend/websocket/server.py`](backend/websocket/server.py) receives the HTTP POST request from the `stream_consumer`.
- **Mechanism**:
    - It takes the JSON data from the request.
    - It then broadcasts this data to **all** currently connected WebSocket clients. This is the "push" mechanism that enables real-time updates.

### Step 2.5: Display on Screen (Frontend)

- **Service**: `web_dashboard`
- **Action**: A user opens `http://localhost:3000` in their web browser.
- **Mechanism**:
    - The browser loads the React application (`index.html`, JavaScript, CSS).
    - As part of its initialization, the React app's `useWebSocket` hook (in [`frontend/hooks/useWebSocket.ts`](frontend/hooks/useWebSocket.ts)) establishes a WebSocket connection to the backend `websocket_server`.
    - The frontend now has an open, persistent connection to the server.
    - When the `websocket_server` broadcasts the stock trade message (from step 2.4), the frontend receives it.
    - The JavaScript code parses the incoming JSON message. Based on the topic (`stock_trades`), it updates the state of the `StockTradesPanel` component ([`frontend/components/StockTradesPanel.tsx`](frontend/components/StockTradesPanel.tsx)).
    - React detects the state change and re-renders the `StockTradesPanel` component, causing the new stock trade data to instantly appear on the user's screen in the corresponding UI element.

This entire process, from generation to display, happens in milliseconds for each message, creating the illusion of a continuous, live data stream on the dashboard for all three topics simultaneously.