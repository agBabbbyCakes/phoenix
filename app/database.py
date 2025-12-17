"""Database module for rental persistence using SQLite."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .models import BotRental, RentalStatus, RentalDuration, PaymentMethod


class RentalDatabase:
    """SQLite database for storing bot rentals."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'rentals.db' in project root.
        """
        if db_path is None:
            # Use project root directory
            project_root = Path(__file__).resolve().parent.parent
            db_path = str(project_root / "rentals.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rentals (
                    id TEXT PRIMARY KEY,
                    bot_id TEXT NOT NULL,
                    bot_name TEXT NOT NULL,
                    user_id TEXT,
                    duration TEXT NOT NULL,
                    price REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT NOT NULL,
                    rented_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rentals_bot_id ON rentals(bot_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rentals_user_id ON rentals(user_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rentals_expires_at ON rentals(expires_at)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_rental(self, rental: BotRental) -> str:
        """Create a new rental record.
        
        Args:
            rental: BotRental object to store
            
        Returns:
            Rental ID
        """
        rental_id = rental.id or f"rental_{rental.bot_id}_{int(rental.rented_at.timestamp())}"
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO rentals (
                    id, bot_id, bot_name, user_id, duration, price,
                    payment_method, status, rented_at, expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rental_id,
                rental.bot_id,
                rental.bot_name,
                rental.user_id,
                rental.duration.value,
                rental.price,
                rental.payment_method.value,
                rental.status.value,
                rental.rented_at.isoformat(),
                rental.expires_at.isoformat(),
                rental.created_at.isoformat()
            ))
            conn.commit()
        
        return rental_id
    
    def get_rental(self, rental_id: str) -> Optional[BotRental]:
        """Get a rental by ID.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            BotRental object or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM rentals WHERE id = ?
            """, (rental_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_rental(row)
    
    def get_active_rentals(self, user_id: Optional[str] = None) -> List[BotRental]:
        """Get all active rentals.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active BotRental objects
        """
        now = datetime.now(timezone.utc).isoformat()
        
        with self._get_connection() as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT * FROM rentals
                    WHERE status = ? AND expires_at > ? AND (user_id IS NULL OR user_id = ?)
                    ORDER BY rented_at DESC
                """, (RentalStatus.ACTIVE.value, now, user_id))
            else:
                cursor = conn.execute("""
                    SELECT * FROM rentals
                    WHERE status = ? AND expires_at > ?
                    ORDER BY rented_at DESC
                """, (RentalStatus.ACTIVE.value, now))
            
            rows = cursor.fetchall()
            return [self._row_to_rental(row) for row in rows]
    
    def get_rentals_by_bot(self, bot_id: str, user_id: Optional[str] = None) -> List[BotRental]:
        """Get all rentals for a specific bot.
        
        Args:
            bot_id: Bot ID
            user_id: Optional user ID to filter by
            
        Returns:
            List of BotRental objects
        """
        with self._get_connection() as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT * FROM rentals
                    WHERE bot_id = ? AND (user_id IS NULL OR user_id = ?)
                    ORDER BY rented_at DESC
                """, (bot_id, user_id))
            else:
                cursor = conn.execute("""
                    SELECT * FROM rentals
                    WHERE bot_id = ?
                    ORDER BY rented_at DESC
                """, (bot_id,))
            
            rows = cursor.fetchall()
            return [self._row_to_rental(row) for row in rows]
    
    def update_rental_status(self, rental_id: str, status: RentalStatus) -> bool:
        """Update rental status.
        
        Args:
            rental_id: Rental ID
            status: New status
            
        Returns:
            True if updated, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE rentals
                SET status = ?
                WHERE id = ?
            """, (status.value, rental_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def cancel_rental(self, rental_id: str) -> bool:
        """Cancel a rental.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            True if cancelled, False if not found
        """
        return self.update_rental_status(rental_id, RentalStatus.CANCELLED)
    
    def expire_rentals(self) -> int:
        """Mark expired rentals as expired.
        
        Returns:
            Number of rentals expired
        """
        now = datetime.now(timezone.utc).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE rentals
                SET status = ?
                WHERE status = ? AND expires_at <= ?
            """, (RentalStatus.EXPIRED.value, RentalStatus.ACTIVE.value, now))
            conn.commit()
            return cursor.rowcount
    
    def _row_to_rental(self, row: sqlite3.Row) -> BotRental:
        """Convert database row to BotRental object.
        
        Args:
            row: SQLite row object
            
        Returns:
            BotRental object
        """
        return BotRental(
            id=row["id"],
            bot_id=row["bot_id"],
            bot_name=row["bot_name"],
            user_id=row["user_id"],
            duration=RentalDuration(row["duration"]),
            price=row["price"],
            payment_method=PaymentMethod(row["payment_method"]),
            status=RentalStatus(row["status"]),
            rented_at=datetime.fromisoformat(row["rented_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )


# Global database instance
_db_instance: Optional[RentalDatabase] = None


def get_database(db_path: Optional[str] = None) -> RentalDatabase:
    """Get or create database instance.
    
    Args:
        db_path: Optional database path. If None, uses settings or default.
    
    Returns:
        RentalDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        # Try to get path from settings if available
        try:
            from .config import settings
            db_path = db_path or settings.database_path
        except Exception:
            pass
        _db_instance = RentalDatabase(db_path)
    return _db_instance

