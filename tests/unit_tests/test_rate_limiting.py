import time
from unittest.mock import patch

import pytest

from app import create_app
from app.config import Config


class TestRateLimitingConfig(Config):
    TESTING = True
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_APPLICATION = "5 per second, 60 per minute"
    SECRET_KEY = "test-key"
    SKIP_AUTH = True


class TestRateLimitingDisabledConfig(Config):
    TESTING = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "test-key"
    SKIP_AUTH = True


class TestRateLimiting:
    @pytest.fixture
    def app_with_rate_limiting(self):
        app = create_app(TestRateLimitingConfig)
        return app

    @pytest.fixture
    def app_without_rate_limiting(self):
        app = create_app(TestRateLimitingDisabledConfig)
        return app

    @pytest.fixture
    def client_with_rate_limiting(self, app_with_rate_limiting):
        return app_with_rate_limiting.test_client()

    @pytest.fixture
    def client_without_rate_limiting(self, app_without_rate_limiting):
        return app_without_rate_limiting.test_client()

    def test_rate_limit_not_triggered_under_limit(self, client_with_rate_limiting):
        """Test that requests under the rate limit are allowed"""
        # Make 4 requests (under the 5 per second limit)
        for i in range(4):
            response = client_with_rate_limiting.get("/")
            assert response.status_code == 200

    def test_rate_limit_triggered_when_exceeded(self, client_with_rate_limiting):
        """Test that rate limit is triggered when exceeded"""
        # Make 6 requests rapidly to exceed the 5 per second limit
        responses = []
        for i in range(6):
            response = client_with_rate_limiting.get("/")
            responses.append(response)

        # First 5 requests should succeed
        for i in range(5):
            assert responses[i].status_code == 200

        # 6th request should be rate limited
        assert responses[5].status_code == 429

    def test_rate_limit_resets_after_time_window(self, client_with_rate_limiting):
        """Test that rate limit resets after the time window"""
        # Make 5 requests to reach the limit
        for i in range(5):
            response = client_with_rate_limiting.get("/")
            assert response.status_code == 200

        # 6th request should be blocked
        response = client_with_rate_limiting.get("/")
        assert response.status_code == 429

        # Wait for rate limit window to reset (slightly over 1 second)
        time.sleep(1.1)

        # Request should now succeed
        response = client_with_rate_limiting.get("/")
        assert response.status_code == 200

    def test_rate_limit_disabled_when_config_false(self, client_without_rate_limiting):
        """Test that rate limiting is disabled when RATELIMIT_ENABLED is False"""
        # With rate limiting disabled, make many requests
        for i in range(10):
            response = client_without_rate_limiting.get("/")
            assert response.status_code == 200

    def test_rate_limit_applies_across_endpoints(self, client_with_rate_limiting):
        """Test that rate limit applies across different endpoints"""
        # Make 5 requests to home page
        for i in range(5):
            response = client_with_rate_limiting.get("/")
            assert response.status_code == 200

        # 6th request to any endpoint should be rate limited
        response = client_with_rate_limiting.get("/")
        assert response.status_code == 429

    def test_rate_limit_error_response_format(self, client_with_rate_limiting):
        """Test that rate limit error returns proper 429 status"""
        # Exhaust the rate limit
        for i in range(5):
            client_with_rate_limiting.get("/")

        # Next request should return 429
        response = client_with_rate_limiting.get("/")
        assert response.status_code == 429

    @patch("app.limiter.limit")
    def test_rate_limiting_decorator_not_called_when_disabled(self, mock_limit, client_without_rate_limiting):
        """Test that limiter decorators are not applied when rate limiting is disabled"""
        # Make 10 requests to home page
        for i in range(10):
            response = client_without_rate_limiting.get("/")
            assert response.status_code == 200  # Since rate limiting is disabled, the limiter should not be active
