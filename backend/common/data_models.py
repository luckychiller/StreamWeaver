"""
Data models using Python dataclasses for type-safe data structures.
Design Pattern: Data Transfer Object (DTO) - Immutable data containers for inter-service communication.
"""
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class StockTrade:
    """Represents a stock trade transaction."""
    timestamp: str
    symbol: str
    type: str  # BUY or SELL
    quantity: int
    price: float

@dataclass
class SocialPost:
    """Represents a social media post."""
    timestamp: str
    user: str
    post_id: str
    content: str
    hashtags: List[str]
    sentiment: str

@dataclass
class ServerLog:
    """Represents a server log entry."""
    timestamp: str
    service: str
    level: str
    message: str
    ip: str

@dataclass
class ProcessedData:
    """Container for processed data with metadata."""
    original: object
    processed_timestamp: str
    # Add other common fields if needed