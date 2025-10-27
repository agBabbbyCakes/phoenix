from __future__ import annotations

import asyncio
from typing import Optional


class SSEBroker:
    """In-memory pub/sub broker for SSE fans out messages to subscribers.

    Subscribers receive JSON strings via their dedicated asyncio.Queue.
    """

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    async def publish(self, message: str) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)
        for q in subscribers:
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                # drop for slow consumers
                pass


async def client_event_stream(request, broker: SSEBroker):
    """SSE generator for a single client subscribing to the broker."""
    queue = await broker.subscribe()
    try:
        yield {"event": "ping", "data": "ready"}
        while True:
            if request is not None and hasattr(request, 'is_disconnected'):
                try:
                    if await request.is_disconnected():
                        break
                except Exception:
                    # Handle any errors checking disconnection
                    break
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield {"event": "metrics_update", "data": msg}
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "keepalive"}
    finally:
        await broker.unsubscribe(queue)


