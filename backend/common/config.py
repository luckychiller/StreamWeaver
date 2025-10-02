"""
Configuration module using Singleton pattern for centralized settings management.
Provides environment-based configuration with sensible defaults.
"""
import os

class Config:
    """
    Singleton-like configuration class.
    Design Pattern: Singleton - Ensures single source of configuration truth.
    """
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    WEBSOCKET_SERVER_URL = os.getenv('WEBSOCKET_SERVER_URL', 'http://localhost:8080')

    # Producer configs
    STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    SERVICES = ['auth_api', 'user_service', 'payment_gateway', 'notification_service', 'data_processor']
    LEVELS = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    SENTIMENTS = ['positive', 'neutral', 'negative']
    CONGESTION_LEVEL =  ["light", "moderate", "heavy", "severe"]
    TRAFFIC_DIRECTION = ["northbound", "southbound", "eastbound", "westbound"]
    TRAFFIC_LOCATION = ["brooklyn_bridge", "Manhattan", "queens_crossing", "bronx_highway", "staten_island_ferry"]
    
    # Topics
    STOCK_TRADES_TOPIC = 'stock_trades'
    SOCIAL_FEED_TOPIC = 'social_feed'
    SERVER_LOGS_TOPIC = 'server_logs'
    TRAFFIC_DATA_TOPIC = 'traffic_data'