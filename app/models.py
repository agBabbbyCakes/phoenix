from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MetricsEvent(BaseModel):
    timestamp: datetime = Field(..., description="UTC timestamp of the metric event")
    bot_name: str = Field(..., description="Name of the bot emitting the event")
    latency_ms: int = Field(..., ge=0, description="Latency in milliseconds")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Success rate 0-100%")
    tx_hash: str = Field(..., description="Shortened transaction hash")
    error: Optional[str] = Field(default=None, description="Optional error message")
    status: Optional[str] = Field(default=None, description="Optional status: ok|warning|critical")
    profit: Optional[float] = Field(default=None, description="Optional profit metric for demo")


