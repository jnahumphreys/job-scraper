import os
from typing import Optional


class Settings:
    """Application configuration settings"""

    # Proxy settings
    USE_PROXIES: bool = os.getenv('USE_PROXIES', 'true').lower() == 'true'
    PROXY_UPDATE_INTERVAL: int = int(
        os.getenv('PROXY_UPDATE_INTERVAL', '300'))  # 5 minutes
    MAX_PROXY_WORKERS: int = int(os.getenv('MAX_PROXY_WORKERS', '20'))
    MAX_WORKING_PROXIES: int = int(os.getenv('MAX_WORKING_PROXIES', '10'))

    # Fallback behavior (defaults to false to prevent rate limiting)
    PROXY_FALLBACK_ENABLED: bool = os.getenv(
        'PROXY_FALLBACK_ENABLED', 'false').lower() == 'true'


settings = Settings()
