"""FastAPI dependencies."""
from __future__ import annotations

from fastapi import Request

from app.data import DataStore
from app.sse import SSEBroker


def get_store(request: Request) -> DataStore:
    """Get DataStore from app state."""
    return request.app.state.store


def get_broker(request: Request) -> SSEBroker:
    """Get SSEBroker from app state."""
    return request.app.state.broker


