from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MetricsEvent(BaseModel):
    timestamp: datetime = Field(..., description="UTC timestamp of the metric event")
    bot_name: str = Field(..., description="Name of the bot emitting the event")
    latency_ms: int = Field(..., ge=0, description="Latency in milliseconds")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Success rate 0-100%")
    tx_hash: str = Field(..., description="Shortened transaction hash")
    error: Optional[str] = Field(default=None, description="Optional error message")
    status: Optional[str] = Field(default=None, description="Optional status: ok|warning|critical")
    profit: Optional[float] = Field(default=None, description="Optional profit metric for demo")


class RentalDuration(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    CRYPTO = "crypto"
    PAYPAL = "paypal"


class RentalStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class BotRental(BaseModel):
    id: Optional[str] = Field(default=None, description="Rental ID")
    bot_id: str = Field(..., description="Bot ID being rented")
    bot_name: str = Field(..., description="Bot name")
    user_id: Optional[str] = Field(default=None, description="User ID (for multi-user support)")
    duration: RentalDuration = Field(..., description="Rental duration")
    price: float = Field(..., ge=0, description="Rental price")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    status: RentalStatus = Field(default=RentalStatus.PENDING, description="Rental status")
    rented_at: datetime = Field(default_factory=datetime.utcnow, description="Rental start time")
    expires_at: datetime = Field(..., description="Rental expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rental creation time")


class RentalRequest(BaseModel):
    bot_id: str = Field(..., description="Bot ID to rent")
    duration: RentalDuration = Field(..., description="Rental duration")
    payment_method: PaymentMethod = Field(..., description="Payment method")


