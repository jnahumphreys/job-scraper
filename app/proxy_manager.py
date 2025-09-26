import requests
import logging
import time
from typing import List, Optional
from urllib.parse import urlparse
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ProxyManager:
    """Manages free proxy lists and validation"""

    def __init__(self):
        self.proxies: List[str] = []
        self.working_proxies: List[str] = []
        self.last_update = 0
        self.update_interval = 300  # 5 minutes
        self._lock = threading.Lock()

    def _fetch_free_proxies(self) -> List[str]:
        """Fetch free proxies from Proxifly"""
        proxy_urls = [
            "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
            "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/US/data.txt",
        ]

        all_proxies = []

        for url in proxy_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    # Format as http://ip:port
                    formatted_proxies = [
                        f"http://{proxy.strip()}" for proxy in proxies if proxy.strip()]
                    all_proxies.extend(formatted_proxies)
                    logger.info(
                        f"Fetched {len(formatted_proxies)} proxies from {url}")
            except Exception as e:
                logger.warning(f"Failed to fetch proxies from {url}: {e}")

        # Remove duplicates
        return list(set(all_proxies))

    def _test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            test_urls = ["http://httpbin.org/ip", "http://icanhazip.com"]

            for test_url in test_urls:
                response = requests.get(
                    test_url,
                    proxies={"http": proxy, "https": proxy},
                    timeout=timeout
                )

                if response.status_code == 200:
                    return True

        except Exception:
            pass

        return False

    def _validate_proxies(self, proxies: List[str], max_workers: int = 20) -> List[str]:
        """Validate proxies concurrently"""
        working_proxies = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(
                self._test_proxy, proxies[:50])  # Test first 50

            for proxy, is_working in zip(proxies[:50], results):
                if is_working:
                    working_proxies.append(proxy)
                    logger.debug(f"✅ Proxy working: {proxy}")

                    # Stop after finding enough working proxies
                    if len(working_proxies) >= 10:
                        break

        logger.info(f"Found {len(working_proxies)} working proxies")
        return working_proxies

    def get_proxy_list(self, force_refresh: bool = False) -> Optional[List[str]]:
        """Get list of working proxies"""
        current_time = time.time()

        with self._lock:
            # Check if we need to update
            if (force_refresh or
                current_time - self.last_update > self.update_interval or
                    not self.working_proxies):

                logger.info("Refreshing proxy list...")

                # Fetch new proxies
                fresh_proxies = self._fetch_free_proxies()

                if fresh_proxies:
                    # Validate proxies
                    self.working_proxies = self._validate_proxies(
                        fresh_proxies)
                    self.last_update = current_time

                    if self.working_proxies:
                        logger.info(
                            f"Updated proxy list with {len(self.working_proxies)} working proxies")
                    else:
                        logger.warning("No working proxies found")
                else:
                    logger.warning("Failed to fetch any proxies")

            return self.working_proxies if self.working_proxies else None


# Global proxy manager instance
proxy_manager = ProxyManager()
