"""Tests for security fixes validation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.violet_pool_controller.api import VioletPoolAPI
from custom_components.violet_pool_controller.utils_sanitizer import InputSanitizer
from custom_components.violet_pool_controller.const import API_SET_CONFIG


class TestSecurityFixes:
    """Test critical security fixes implementation."""

    @pytest.fixture
    def mock_session(self):
        """Create mock aiohttp session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def api(self, mock_session):
        """Create API instance with mocked session."""
        return VioletPoolAPI(
            host="192.168.1.100",
            session=mock_session,
            username="testuser",
            password="testpass",
            use_ssl=True,
            timeout=10,
            max_retries=3,
        )

    def test_url_security_srf_protection(self):
        """Test SSRF protection in URL construction."""
        api = VioletPoolAPI.__new__(VioletPoolAPI)
        
        # Test valid host
        valid_url = api._build_secure_base_url("192.168.1.100", True)
        assert valid_url.startswith("https://192.168.1.100")
        
        # Test SSRF attempts - should raise ValueError
        with pytest.raises(ValueError, match="internal network"):
            api._build_secure_base_url("127.0.0.1", True)
        
        with pytest.raises(ValueError, match="internal network"):
            api._build_secure_base_url("169.254.169.254", True)
        
        with pytest.raises(ValueError, match="Invalid hostname"):
            api._build_secure_base_url("../../../etc/passwd", True)
        
        with pytest.raises(ValueError, match="Invalid hostname"):
            api._build_secure_base_url("', DROP TABLE users; --", True)

    def test_input_sanitization_config(self):
        """Test configuration input sanitization."""
        malicious_config = {
            "key; DROP TABLE users; --": "value",
            "../../../etc/passwd": "malicious",
            "<script>alert('xss')</script>": "xss_attempt",
            "valid_key": "valid_value",
            "numeric_test": 123.45,
        }
        
        # Test InputSanitizer directly
        sanitized_config = {}
        for key, value in malicious_config.items():
            try:
                sanitized_key = InputSanitizer.validate_api_parameter(str(key))
                if isinstance(value, str):
                    sanitized_value = InputSanitizer.sanitize_string(value, max_length=1000)
                elif isinstance(value, (int, float)):
                    sanitized_value = InputSanitizer.sanitize_numeric(value)
                else:
                    sanitized_value = InputSanitizer.sanitize_string(str(value))
                sanitized_config[sanitized_key] = sanitized_value
            except ValueError:
                # Malicious keys should be rejected
                pass
        
        # Valid key should pass through
        assert "valid_key" in sanitized_config
        assert sanitized_config["valid_key"] == "valid_value"
        assert "numeric_test" in sanitized_config
        assert sanitized_config["numeric_test"] == 123.45
        
        # Malicious keys should be rejected
        assert not any("DROP TABLE" in key for key in sanitized_config.keys())
        assert not any("../" in key for key in sanitized_config.keys())
        assert not any("<script>" in key for key in sanitized_config.keys())

    def test_numeric_sanitization(self):
        """Test numeric sanitization function."""
        # Valid numbers
        assert InputSanitizer.sanitize_numeric(123) == 123.0
        assert InputSanitizer.sanitize_numeric(45.67) == 45.67
        assert InputSanitizer.sanitize_numeric("123") == 123.0
        assert InputSanitizer.sanitize_numeric("45.67") == 45.67
        assert InputSanitizer.sanitize_numeric("-123.45") == -123.45
        
        # Invalid inputs
        assert InputSanitizer.sanitize_numeric("abc") == 0.0
        assert InputSanitizer.sanitize_numeric("") == 0.0
        assert InputSanitizer.sanitize_numeric("12a3b") == 123.0
        assert InputSanitizer.sanitize_numeric(None) == 0.0

    def test_ssl_context_creation(self):
        """Test SSL context creation with validation."""
        # Test SSL context creation would be in config_flow
        # For now, test that URL construction respects SSL flag
        api = VioletPoolAPI.__new__(VioletPoolAPI)
        
        # SSL enabled
        ssl_url = api._build_secure_base_url("example.com", True)
        assert ssl_url.startswith("https://")
        
        # SSL disabled
        http_url = api._build_secure_base_url("example.com", False)
        assert http_url.startswith("http://")

    async def test_config_with_sanitization(self, api):
        """Test set_config method with sanitization."""
        malicious_config = {
            "malicious;key": "value1",
            "valid_key": "valid_value",
            "numeric_key": 42,
            "another_valid": "test123"
        }
        
        # Mock the request to avoid actual API calls
        with patch.object(api, '_request') as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            try:
                await api.set_config(malicious_config)
                
                # Check that _request was called
                mock_request.assert_called_once()
                
                # Get the sanitized config that was passed
                call_args = mock_request.call_args
                sanitized_config = call_args[1]['json_payload']
                
                # Valid keys should be present
                assert "valid_key" in sanitized_config
                assert "numeric_key" in sanitized_config
                assert sanitized_config["numeric_key"] == 42.0
                
                # Malicious keys should be rejected or sanitized
                assert not any(";" in key for key in sanitized_config.keys())
                
            except Exception as e:
                # Expected for malicious input
                assert "Invalid configuration parameter" in str(e)

    def test_hostname_validation_patterns(self):
        """Test various hostname validation patterns."""
        api = VioletPoolAPI.__new__(VioletPoolAPI)
        
        # Valid hostnames
        valid_hosts = [
            "192.168.1.100",
            "pool-controller.local",
            "violet.example.com",
            "192.0.2.1"
        ]
        
        for host in valid_hosts:
            try:
                result = api._build_secure_base_url(host, True)
                assert result is not None
                assert result.startswith("https://")
            except ValueError:
                pytest.fail(f"Valid host {host} was rejected")
        
        # Invalid hostnames
        invalid_hosts = [
            "127.0.0.1",
            "169.254.169.254",
            "10.0.0.1",
            "172.16.0.1",
            "localhost",
            "evil.com@internal",
            "user:pass@192.168.1.1",
            "../etc/passwd",
            "' OR 1=1 --",
            "''; DROP TABLE users; --"
        ]
        
        for host in invalid_hosts:
            with pytest.raises(ValueError):
                api._build_secure_base_url(host, True)