"""Configuration management using Pydantic Settings."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

# Try to import BaseSettings from pydantic_settings (Pydantic v2)
# Fall back to pydantic (Pydantic v1) if not available
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    try:
        from pydantic import BaseSettings, Field
        PYDANTIC_AVAILABLE = True
    except ImportError:
        PYDANTIC_AVAILABLE = False
        # Create a dummy Field function for fallback
        def Field(*args, **kwargs):
            return kwargs.get('default', None)
        # Create a simple BaseSettings fallback
        class BaseSettings:
            pass


if PYDANTIC_AVAILABLE:
    class Settings(BaseSettings):
        """Application settings loaded from environment variables."""
        
        # Server settings
        host: str = Field(default="127.0.0.1", description="Server host")
        port: int = Field(default=8000, description="Server port")
        reload: bool = Field(default=False, description="Enable auto-reload in development")
        
        # CORS settings
        cors_origins: List[str] = Field(
            default_factory=lambda: ["http://localhost:8000", "http://127.0.0.1:8000"],
            description="Allowed CORS origins"
        )
        cors_allow_all: bool = Field(
            default=False,
            description="Allow all origins (development only - security risk in production). Only works when debug=True."
        )
        
        # Database settings
        database_path: Optional[str] = Field(
            default=None,
            description="Path to SQLite database file. If None, uses 'rentals.db' in project root."
        )
        
        # Application settings
        app_name: str = Field(default="Ethereum Bot Monitoring Dashboard", description="Application name")
        app_version: str = Field(default="0.1.0", description="Application version")
        debug: bool = Field(default=False, description="Debug mode")
        
        # Data settings
        max_events: int = Field(default=1000, description="Maximum events to store in memory")
        silverback_log_path: Optional[str] = Field(default=None, description="Path to Silverback JSONL log file")
        force_sample: bool = Field(default=False, description="Force sample/demo mode")
        clean_ui: bool = Field(default=False, description="Clean UI mode (no data publishers)")
        
        # Rate limiting
        rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
        rate_limit_per_minute: int = Field(default=120, description="Requests per minute per IP")
        
        # Logging
        log_level: str = Field(default="INFO", description="Logging level")
        log_file: Optional[str] = Field(default=None, description="Log file path (optional)")
        
        # Ethereum settings
        eth_wss_url: Optional[str] = Field(default=None, description="Ethereum WebSocket URL")
        chainlink_ethusd: Optional[str] = Field(default=None, description="Chainlink ETH/USD contract address")
        
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
    
    settings = Settings()
else:
    # Fallback: use environment variables directly
    from dotenv import load_dotenv
    load_dotenv()
    
    class Settings:
        """Simple settings class using environment variables when pydantic not available."""
        def __init__(self):
            self.host = os.getenv("HOST", "127.0.0.1")
            self.port = int(os.getenv("PORT", "8000"))
            self.reload = os.getenv("RELOAD", "false").lower() in ("1", "true", "yes")
            cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
            self.cors_origins = [x.strip() for x in cors_origins_str.split(",") if x.strip()]
            self.cors_allow_all = os.getenv("CORS_ALLOW_ALL", "false").lower() in ("1", "true", "yes")
            self.app_name = os.getenv("APP_NAME", "Ethereum Bot Monitoring Dashboard")
            self.app_version = os.getenv("APP_VERSION", "0.1.0")
            self.debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")
            self.max_events = int(os.getenv("MAX_EVENTS", "1000"))
            self.silverback_log_path = os.getenv("SILVERBACK_LOG_PATH")
            self.force_sample = os.getenv("FORCE_SAMPLE", "false").lower() in ("1", "true", "yes")
            self.clean_ui = os.getenv("CLEAN_UI", "false").lower() in ("1", "true", "yes")
            self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("1", "true", "yes")
            self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.log_file = os.getenv("LOG_FILE")
            self.eth_wss_url = os.getenv("ETH_WSS_URL")
            self.chainlink_ethusd = os.getenv("CHAINLINK_ETHUSD")
    
    settings = Settings()

