from unittest.mock import Mock, patch, MagicMock
from flask import Response
from app.main.middleware import add_noindex_header, add_no_cache_headers


class TestAddNoindexHeader:
    def test_adds_noindex_header(self):
        response = Mock(spec=Response)
        response.headers = {}

        result = add_noindex_header(response)

        assert response.headers["X-Robots-Tag"] == "noindex"
        assert result == response

    def test_preserves_existing_headers(self):
        response = Mock(spec=Response)
        response.headers = {"Content-Type": "text/html"}

        result = add_noindex_header(response)

        assert response.headers["X-Robots-Tag"] == "noindex"
        assert response.headers["Content-Type"] == "text/html"
        assert result == response

    def test_overwrites_existing_robots_tag(self):
        response = Mock(spec=Response)
        response.headers = {"X-Robots-Tag": "index"}

        result = add_noindex_header(response)

        assert response.headers["X-Robots-Tag"] == "noindex"
        assert result == response


class TestAddNoCacheHeaders:
    def test_adds_no_cache_headers_for_regular_paths(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/some/page"

            result = add_no_cache_headers(response)

            assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
            assert response.headers["Pragma"] == "no-cache"
            assert response.headers["Expires"] == "0"
            assert result == response

    def test_adds_cache_headers_for_assets_paths(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/assets/css/styles.css"

            result = add_no_cache_headers(response)

            assert response.headers["Cache-Control"] == "public, max-age=1800"
            assert response.headers["Pragma"] == "cache"
            assert "Expires" not in response.headers
            assert result == response

    def test_assets_path_variations(self):
        response = Mock(spec=Response)

        test_cases = [
            "/assets/js/script.js",
            "/assets/images/logo.png",
            "/assets/fonts/font.woff",
            "/assets/subfolder/file.css",
        ]

        for path in test_cases:
            response.headers = {}

            with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
                mock_request.path = path

                result = add_no_cache_headers(response)

                assert response.headers["Cache-Control"] == "public, max-age=1800"
                assert response.headers["Pragma"] == "cache"
                assert result == response

    def test_non_assets_path_variations(self):
        test_cases = [
            "/",
            "/home",
            "/form",
            "/api/data",
            "/not-assets/file.js",  # Should not match
            "/some/assets/file.css",  # Should not match (doesn't start with /assets)
        ]

        for path in test_cases:
            response = Mock(spec=Response)
            response.headers = {}

            with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
                mock_request.path = path

                result = add_no_cache_headers(response)

                assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0", (
                    f"Failed for path: {path}"
                )
                assert response.headers["Pragma"] == "no-cache"
                assert response.headers["Expires"] == "0"
                assert result == response

    def test_preserves_existing_headers(self):
        response = Mock(spec=Response)
        response.headers = {"Content-Type": "text/html"}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/some/page"

            result = add_no_cache_headers(response)

            assert response.headers["Content-Type"] == "text/html"
            assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
            assert result == response

    def test_overwrites_existing_cache_headers(self):
        response = Mock(spec=Response)
        response.headers = {"Cache-Control": "max-age=3600", "Pragma": "public"}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/some/page"

            result = add_no_cache_headers(response)

            assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
            assert response.headers["Pragma"] == "no-cache"
            assert response.headers["Expires"] == "0"
            assert result == response

    def test_edge_case_empty_path(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = ""

            result = add_no_cache_headers(response)

            assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
            assert response.headers["Pragma"] == "no-cache"
            assert response.headers["Expires"] == "0"
            assert result == response

    def test_edge_case_root_assets_path(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/assets"

            result = add_no_cache_headers(response)

            assert response.headers["Cache-Control"] == "public, max-age=1800"
            assert response.headers["Pragma"] == "cache"
            assert result == response


class TestMiddlewareIntegration:
    def test_both_middlewares_applied(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/some/page"

            # Apply both middleware functions
            result = add_noindex_header(response)
            result = add_no_cache_headers(result)

            # Check both sets of headers are applied
            assert response.headers["X-Robots-Tag"] == "noindex"
            assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
            assert response.headers["Pragma"] == "no-cache"
            assert response.headers["Expires"] == "0"
            assert result == response

    def test_middlewares_with_assets_path(self):
        response = Mock(spec=Response)
        response.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/assets/style.css"

            # Apply both middleware functions
            result = add_noindex_header(response)
            result = add_no_cache_headers(result)

            # Check both sets of headers are applied
            assert response.headers["X-Robots-Tag"] == "noindex"
            assert response.headers["Cache-Control"] == "public, max-age=1800"
            assert response.headers["Pragma"] == "cache"
            assert "Expires" not in response.headers
            assert result == response

    def test_middleware_order_independence(self):
        response1 = Mock(spec=Response)
        response1.headers = {}
        response2 = Mock(spec=Response)
        response2.headers = {}

        with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
            mock_request.path = "/test/page"

            # Apply in one order
            result1 = add_noindex_header(response1)
            result1 = add_no_cache_headers(result1)

            # Apply in reverse order
            result2 = add_no_cache_headers(response2)
            result2 = add_noindex_header(result2)

            # Both should have the same headers
            assert response1.headers == response2.headers

    def test_real_response_object_compatibility(self, app):
        with app.app_context():
            response = Response("Test content")

            with patch("app.main.middleware.request", new_callable=lambda: MagicMock()) as mock_request:
                mock_request.path = "/test"

                result = add_noindex_header(response)
                result = add_no_cache_headers(result)

                assert result.headers["X-Robots-Tag"] == "noindex"
                assert result.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
                assert result.headers["Pragma"] == "no-cache"
                assert result.headers["Expires"] == "0"
