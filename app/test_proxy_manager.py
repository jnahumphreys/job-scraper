import pytest
from unittest.mock import Mock, patch, MagicMock
from app.proxy_manager import ProxyManager


class TestProxyManager:

    def test_fetch_free_proxies_success(self):
        """Test successful proxy fetching"""
        proxy_manager = ProxyManager()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "1.2.3.4:8080\n5.6.7.8:3128\n9.10.11.12:8080"

        with patch('requests.get', return_value=mock_response):
            proxies = proxy_manager._fetch_free_proxies()

        assert len(proxies) >= 3  # At least the unique proxies
        assert "http://1.2.3.4:8080" in proxies
        assert "http://5.6.7.8:3128" in proxies
        assert "http://9.10.11.12:8080" in proxies

    def test_fetch_free_proxies_failure(self):
        """Test handling of proxy fetching failure"""
        proxy_manager = ProxyManager()

        with patch('requests.get', side_effect=Exception("Network error")):
            proxies = proxy_manager._fetch_free_proxies()

        assert proxies == []

    def test_proxy_validation_success(self):
        """Test successful proxy validation"""
        proxy_manager = ProxyManager()

        with patch.object(proxy_manager, '_test_proxy', return_value=True):
            working = proxy_manager._validate_proxies(
                ["http://1.2.3.4:8080", "http://5.6.7.8:3128"])

        assert len(working) == 2
        assert "http://1.2.3.4:8080" in working
        assert "http://5.6.7.8:3128" in working

    def test_proxy_validation_partial_success(self):
        """Test partial proxy validation success"""
        proxy_manager = ProxyManager()

        def mock_test_proxy(proxy):
            return proxy == "http://1.2.3.4:8080"  # Only first proxy works

        with patch.object(proxy_manager, '_test_proxy', side_effect=mock_test_proxy):
            working = proxy_manager._validate_proxies(
                ["http://1.2.3.4:8080", "http://5.6.7.8:3128"])

        assert len(working) == 1
        assert "http://1.2.3.4:8080" in working

    def test_test_proxy_success(self):
        """Test successful proxy testing"""
        proxy_manager = ProxyManager()

        mock_response = Mock()
        mock_response.status_code = 200

        with patch('requests.get', return_value=mock_response):
            result = proxy_manager._test_proxy("http://1.2.3.4:8080")

        assert result is True

    def test_test_proxy_failure(self):
        """Test proxy testing failure"""
        proxy_manager = ProxyManager()

        with patch('requests.get', side_effect=Exception("Connection failed")):
            result = proxy_manager._test_proxy("http://1.2.3.4:8080")

        assert result is False

    def test_get_proxy_list_with_cache(self):
        """Test proxy list caching"""
        proxy_manager = ProxyManager()
        proxy_manager.working_proxies = ["http://1.2.3.4:8080"]
        proxy_manager.last_update = 999999999999  # Very recent timestamp

        # Should return cached proxies without refresh
        proxies = proxy_manager.get_proxy_list()
        assert proxies == ["http://1.2.3.4:8080"]

    def test_get_proxy_list_force_refresh(self):
        """Test forced proxy list refresh"""
        proxy_manager = ProxyManager()
        proxy_manager.working_proxies = ["http://old.proxy:8080"]

        with patch.object(proxy_manager, '_fetch_free_proxies', return_value=["http://1.2.3.4:8080"]):
            with patch.object(proxy_manager, '_validate_proxies', return_value=["http://1.2.3.4:8080"]):
                proxies = proxy_manager.get_proxy_list(force_refresh=True)

        assert proxies == ["http://1.2.3.4:8080"]

    def test_get_proxy_list_no_working_proxies(self):
        """Test handling when no working proxies are found"""
        proxy_manager = ProxyManager()

        with patch.object(proxy_manager, '_fetch_free_proxies', return_value=["http://1.2.3.4:8080"]):
            with patch.object(proxy_manager, '_validate_proxies', return_value=[]):
                proxies = proxy_manager.get_proxy_list(force_refresh=True)

        assert proxies is None

    def test_fetch_free_proxies_with_different_protocols(self):
        """Test proxy parsing with different protocols"""
        proxy_manager = ProxyManager()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        http://1.2.3.4:8080
        socks4://5.6.7.8:1080
        socks5://9.10.11.12:1080  
        https://13.14.15.16:443
        17.18.19.20:3128
        """

        with patch('requests.get', return_value=mock_response):
            proxies = proxy_manager._fetch_free_proxies()

        # Should only include HTTP proxies and plain IP:port (converted to HTTP)
        assert "http://1.2.3.4:8080" in proxies
        assert "http://17.18.19.20:3128" in proxies
        # Should exclude non-HTTP protocols
        assert not any("socks4://" in proxy for proxy in proxies)
        assert not any("socks5://" in proxy for proxy in proxies)
        assert not any("https://" in proxy for proxy in proxies)

    def test_get_proxy_list_logs_no_working_proxies_warning(self):
        """Test that warning is logged when no working proxies found"""
        proxy_manager = ProxyManager()

        with patch.object(proxy_manager, '_fetch_free_proxies', return_value=["http://1.2.3.4:8080"]):
            with patch.object(proxy_manager, '_validate_proxies', return_value=[]):
                with patch('app.proxy_manager.logger') as mock_logger:
                    proxies = proxy_manager.get_proxy_list(force_refresh=True)

                    # Verify warning was logged (line 128)
                    mock_logger.warning.assert_called_with(
                        "No working proxies found")
                    assert proxies is None

    def test_get_proxy_list_no_proxy_fetch_failure(self):
        """Test when proxy fetching fails completely"""
        proxy_manager = ProxyManager()

        with patch.object(proxy_manager, '_fetch_free_proxies', return_value=[]):
            with patch('app.proxy_manager.logger') as mock_logger:
                proxies = proxy_manager.get_proxy_list(force_refresh=True)

                # Should warn about no proxies being fetched
                mock_logger.warning.assert_called_with(
                    "Failed to fetch any proxies")
                assert proxies is None
