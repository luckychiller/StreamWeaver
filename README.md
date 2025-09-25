# StreamWeaver - Real-Time Data Ingestion Pipeline

StreamWeaver is a high-throughput data ingestion pipeline that simulates real-time data streams (stock trades, social media posts, server logs) using Apache Kafka, processes them, and visualizes the results in a real-time web dashboard.

## Architecture Overview

### Backend Architecture (SOLID & Design Patterns)

The backend follows SOLID principles and implements several design patterns for maintainability and extensibility:

#### **Common Module** (`backend/common/`)
- **`config.py`**: **Singleton Pattern** - Centralized configuration management
- **`data_models.py`**: **Data Transfer Object (DTO) Pattern** - Type-safe data structures using dataclasses
- **`kafka_client.py`**: **Facade Pattern** - Simplified interface to complex Kafka operations

#### **Producers Module** (`backend/producers/`)
- **`base/producer.py`**: **Template Method + Abstract Factory Patterns**
  - Abstract `BaseProducer` defines the production algorithm
  - Concrete implementations (`StockTradeProducer`, `SocialMediaProducer`, `ServerLogProducer`) provide data-specific logic
- **Benefits**: Easy to add new data producers without modifying existing code

#### **Consumer Module** (`backend/consumer/`)
- **`DataTransformer`**: **Strategy Pattern** - Pluggable transformation algorithms per data type
- **`WebSocketPublisher`**: Publisher for broadcasting to clients
- **`StreamConsumer`**: **Observer Pattern** - Reacts to Kafka messages and coordinates processing

### Frontend Architecture
- **React + TypeScript**: Type-safe component development
- **WebSocket Integration**: Real-time data updates
- **Modular Components**: Reusable UI components with single responsibilities

### Infrastructure
- **Docker Compose**: Container orchestration with health checks
- **Kafka + Zookeeper**: Fault-tolerant message queuing
- **AsyncIO**: High-performance concurrent processing

## Design Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Singleton** | `Config` | Single source of configuration |
| **Facade** | `KafkaClient` | Simplify Kafka operations |
| **Template Method** | `BaseProducer` | Define production algorithm skeleton |
| **Abstract Factory** | `BaseProducer` subclasses | Create families of data generators |
| **Strategy** | `DataTransformer` | Pluggable transformation logic |
| **Observer** | `StreamConsumer` | React to Kafka messages |
| **DTO** | Data models | Type-safe data transfer |

## Quick Start

1. Ensure Docker and Docker Compose are installed.

2. Clone the repository and navigate to the project directory.

3. Build and start all services:
   ```bash
   docker-compose up --build
   ```

4. Open your browser and go to `http://localhost:3000` to view the real-time dashboard.

5. The dashboard will display live-updating stock trades, social media posts, and server logs.

## Services

- **Zookeeper**: `localhost:2181`
- **Kafka**: `localhost:9092`
- **WebSocket Server**: `localhost:8080`
- **Dashboard**: `localhost:3000`

## Topics

- `stock_trades`: Real-time stock buy/sell orders
- `social_feed`: Simulated social media posts
- `server_logs`: Mock server access and error logs

## Development

### Backend Structure
```
backend/
├── common/           # Shared utilities and patterns
├── producers/        # Data generation (Template Method pattern)
├── consumer/         # Data processing (Strategy pattern)
└── websocket/        # Real-time broadcasting
```

### Adding New Data Producers
1. Create new class inheriting from `BaseProducer`
2. Implement `generate_data()` method
3. Override `get_key()` if needed for partitioning
4. Add to Docker Compose configuration

### Adding New Transformations
1. Add new method to `DataTransformer`
2. Update `transform_map` in `StreamConsumer`
3. Frontend will automatically handle new message types

### Frontend Development
The frontend is a React + TypeScript application using Vite. To run it standalone for development:

1. Navigate to the `frontend/` directory
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Access at `http://localhost:5173`

For full integration, use the Docker Compose setup which serves the frontend at `http://localhost:3000`.

## Performance

The system is designed to handle 1000+ messages per second with low latency, suitable for real-time analytics and monitoring. Uses asyncio for concurrent processing and Kafka for scalable messaging.

## SOLID Principles Applied

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: New features added without modifying existing code
- **Liskov Substitution**: Subclasses can replace base classes
- **Interface Segregation**: Focused, minimal interfaces
- **Dependency Inversion**: Depends on abstractions, not concretions

## Stopping the System

```bash
docker-compose down