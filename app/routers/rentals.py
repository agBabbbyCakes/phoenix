"""Bot rental endpoints."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies import get_store
from app.models import RentalRequest, RentalDuration, RentalStatus
from app.database import get_database

router = APIRouter()


@router.post("/api/bots/rent")
async def rent_bot(request: Request, rental_request: RentalRequest) -> JSONResponse:
    """Rent a bot for a specified duration.
    
    Creates a rental record and returns rental information.
    In production, this would integrate with payment processing.
    """
    try:
        store = get_store(request)
        
        # Calculate expiration time based on duration
        now = datetime.now(timezone.utc)
        if rental_request.duration == RentalDuration.HOURLY:
            expires_at = now + timedelta(hours=1)
            base_price = 0.5  # Base hourly price
        elif rental_request.duration == RentalDuration.DAILY:
            expires_at = now + timedelta(days=1)
            base_price = 12.0  # Daily price
        elif rental_request.duration == RentalDuration.MONTHLY:
            expires_at = now + timedelta(days=30)
            base_price = 300.0  # Monthly price (with discount)
        else:
            return JSONResponse({"status": "error", "message": "Invalid duration"}, status_code=400)
        
        # Get bot info to calculate price
        bot_stats = {}
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == rental_request.bot_id:
                bot_stats["bot_name"] = event.bot_name
                bot_stats["success_rate"] = event.success_rate
                break
        
        # Calculate performance-based pricing
        # Higher success rate = higher price
        performance_multiplier = 1.0
        if bot_stats.get("success_rate", 0) > 95:
            performance_multiplier = 1.5  # Premium bots cost 50% more
        elif bot_stats.get("success_rate", 0) > 90:
            performance_multiplier = 1.25
        elif bot_stats.get("success_rate", 0) > 80:
            performance_multiplier = 1.0
        else:
            performance_multiplier = 0.8  # Lower performance = discount
        
        final_price = base_price * performance_multiplier
        
        # Create rental record
        from app.models import BotRental
        rental = BotRental(
            bot_id=rental_request.bot_id,
            bot_name=bot_stats.get("bot_name", rental_request.bot_id),
            duration=rental_request.duration,
            price=final_price,
            payment_method=rental_request.payment_method,
            status=RentalStatus.ACTIVE,
            rented_at=now,
            expires_at=expires_at
        )
        
        # Store rental in database
        db = get_database()
        rental_id = db.create_rental(rental)
        rental.id = rental_id
        
        return JSONResponse({
            "status": "success",
            "rental": {
                "id": rental_id,
                "bot_id": rental.bot_id,
                "bot_name": rental.bot_name,
                "duration": rental.duration.value,
                "price": round(rental.price, 2),
                "performance_multiplier": round(performance_multiplier, 2),
                "status": rental.status.value,
                "rented_at": rental.rented_at.isoformat(),
                "expires_at": rental.expires_at.isoformat()
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@router.get("/api/bots/rentals")
async def get_rentals(request: Request) -> JSONResponse:
    """Get all active rentals for the current user.
    
    Returns list of active bot rentals with performance metrics.
    """
    try:
        store = get_store(request)
        # Get rentals from database
        db = get_database()
        # Expire old rentals first
        db.expire_rentals()
        
        # Get active rentals (user_id can be added later for multi-user support)
        active_rentals = db.get_active_rentals()
        
        now = datetime.now(timezone.utc)
        rentals = []
        
        for rental in active_rentals:
            # Get current bot performance
            bot_stats = {}
            events = list(store.events)
            for event in events:
                if event.bot_name.lower().replace(" ", "-") == rental.bot_id:
                    bot_stats["success_rate"] = event.success_rate
                    bot_stats["latency_ms"] = event.latency_ms
                    break
            
            rentals.append({
                "id": rental.id or f"rental_{rental.bot_id}_{int(rental.rented_at.timestamp())}",
                "bot_id": rental.bot_id,
                "bot_name": rental.bot_name,
                "duration": rental.duration.value,
                "price": rental.price,
                "status": rental.status.value,
                "rented_at": rental.rented_at.isoformat(),
                "expires_at": rental.expires_at.isoformat(),
                "time_remaining": int((rental.expires_at - now).total_seconds()),
                "current_performance": {
                    "success_rate": bot_stats.get("success_rate", 0),
                    "latency_ms": bot_stats.get("latency_ms", 0)
                }
            })
        
        return JSONResponse({
            "status": "success",
            "rentals": rentals,
            "count": len(rentals)
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@router.get("/api/bots/{bot_id}/rental-info")
async def get_bot_rental_info(request: Request, bot_id: str) -> JSONResponse:
    """Get rental information and pricing for a specific bot.
    
    Returns pricing tiers and availability.
    """
    try:
        store = get_store(request)
        # Get bot stats
        bot_stats = {}
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == bot_id:
                bot_stats["bot_name"] = event.bot_name
                break
        
        # Calculate pricing based on bot type/strategy and performance
        strategy = "arbitrage"  # Default
        if "mev" in bot_id.lower():
            strategy = "mev"
        elif "trade" in bot_id.lower() or "snipe" in bot_id.lower():
            strategy = "trading"
        elif "monitor" in bot_id.lower():
            strategy = "monitoring"
        
        base_prices = {
            "arbitrage": 0.5,
            "mev": 0.8,
            "trading": 0.6,
            "monitoring": 0.3,
            "defi": 0.7,
            "nft": 0.4
        }
        
        # Get bot performance metrics
        success_rate = 0
        latency_ms = 0
        events = list(store.events)
        for event in events:
            if event.bot_name.lower().replace(" ", "-") == bot_id:
                success_rate = event.success_rate
                latency_ms = event.latency_ms
                break
        
        # Performance-based pricing multiplier
        performance_multiplier = 1.0
        if success_rate > 95:
            performance_multiplier = 1.5  # Premium performance
        elif success_rate > 90:
            performance_multiplier = 1.25
        elif success_rate > 80:
            performance_multiplier = 1.0
        else:
            performance_multiplier = 0.8  # Discount for lower performance
        
        hourly_price = base_prices.get(strategy, 0.5) * performance_multiplier
        daily_price = hourly_price * 24
        monthly_price = hourly_price * 24 * 30 * 0.8  # 20% discount for monthly
        
        return JSONResponse({
            "status": "success",
            "bot_id": bot_id,
            "bot_name": bot_stats.get("bot_name", bot_id),
            "pricing": {
                "hourly": round(hourly_price, 2),
                "daily": round(daily_price, 2),
                "monthly": round(monthly_price, 2),
                "performance_multiplier": round(performance_multiplier, 2),
                "base_strategy": strategy
            },
            "performance": {
                "success_rate": round(success_rate, 2),
                "latency_ms": latency_ms
            },
            "available": True
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@router.delete("/api/bots/rentals/{rental_id}")
async def cancel_rental(rental_id: str) -> JSONResponse:
    """Cancel an active rental.
    
    Marks rental as cancelled and processes refund if applicable.
    """
    try:
        # Cancel rental in database
        db = get_database()
        success = db.cancel_rental(rental_id)
        
        if success:
            return JSONResponse({
                "status": "success",
                "message": f"Rental {rental_id} cancelled successfully",
                "rental_id": rental_id
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": f"Rental {rental_id} not found"
            }, status_code=404)
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=400)

