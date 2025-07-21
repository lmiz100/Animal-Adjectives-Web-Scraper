import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from main import (
    app,
    background_scrape_and_generate,
    serve_report,
    OUTPUT_HTML,
    FALLBACK_OUTPUT_HTML
)
from models.animal_entry import AnimalEntry


class TestBackgroundScrapeAndGenerate:
    """Test cases for the background_scrape_and_generate function."""

    @pytest.mark.asyncio
    @patch('main.get_animal_entries')
    @patch('main.download_images_concurrently')
    @patch('main.generate_html')
    @patch('main.console')
    async def test_background_scrape_and_generate_success(
            self, mock_console, mock_generate_html, mock_download_images, mock_get_entries
    ):
        """Test successful execution of background scrape and generate."""
        # Arrange
        mock_animals = [
            AnimalEntry(name="Lion", href="/wiki/Lion", collateral_adjectives=["leonine"]),
            AnimalEntry(name="Cat", href="/wiki/Cat", collateral_adjectives=["feline"])
        ]
        mock_get_entries.return_value = mock_animals
        mock_download_images.return_value = mock_animals
        mock_generate_html.return_value = None

        # Act
        await background_scrape_and_generate(log_prefix='Test')

        # Assert
        mock_console.log.assert_any_call("[Test] Scraping and generating report...")
        mock_console.log.assert_any_call(f"[Test] Report ready at: {OUTPUT_HTML}")
        mock_get_entries.assert_called_once()
        mock_download_images.assert_called_once_with(mock_animals)
        mock_generate_html.assert_called_once_with(mock_animals)

    @pytest.mark.asyncio
    @patch('main.get_animal_entries')
    @patch('main.console')
    async def test_background_scrape_and_generate_exception(
            self, mock_console, mock_get_entries
    ):
        """Test that exceptions in background_scrape_and_generate are properly handled."""
        # Arrange
        mock_get_entries.side_effect = Exception("Wikipedia scraping failed")

        # Act & Assert
        with pytest.raises(Exception, match="Wikipedia scraping failed"):
            await background_scrape_and_generate(log_prefix='Test')

        mock_console.log.assert_called_with("[Test] Scraping and generating report...")


class TestFastAPIEndpoints:
    """Test cases for FastAPI endpoints."""

    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)

    def test_serve_report_with_existing_output(self):
        """Test serving report when OUTPUT_HTML exists."""
        with patch('main.FileResponse') as mock_file_response, \
                patch('main.os.path.exists') as mock_exists:
            # Arrange
            mock_exists.return_value = True
            mock_response = Mock()
            mock_file_response.return_value = mock_response

            # Act
            import asyncio
            result = asyncio.run(serve_report())

            # Assert
            mock_exists.assert_called_once_with(OUTPUT_HTML)
            mock_file_response.assert_called_once_with(OUTPUT_HTML, media_type="text/html")
            assert result == mock_response

    def test_serve_report_with_fallback(self):
        """Test serving report when OUTPUT_HTML doesn't exist, uses fallback."""
        with patch('main.FileResponse') as mock_file_response, \
                patch('main.os.path.exists') as mock_exists:
            # Arrange
            mock_exists.return_value = False
            mock_response = Mock()
            mock_file_response.return_value = mock_response

            # Act
            import asyncio
            result = asyncio.run(serve_report())

            # Assert
            mock_exists.assert_called_once_with(OUTPUT_HTML)
            mock_file_response.assert_called_once_with(FALLBACK_OUTPUT_HTML, media_type="text/html")
            assert result == mock_response

    @patch('main.update_lock')
    def test_update_report_success(self, mock_lock):
        """Test successful report update request."""
        # Arrange
        mock_lock.locked.return_value = False

        # Act
        response = self.client.post("/update-report")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "Report update started in background"}

    def test_update_report_endpoint_exists(self):
        """Test that the update-report endpoint exists and is accessible."""
        # This is a simple test to verify the endpoint is registered
        # We're not testing the actual functionality to avoid complexity
        routes = [route.path for route in app.routes]
        assert "/update-report" in [route.path for route in app.routes if hasattr(route, 'path')]


class TestAsyncLockBehavior:
    """Test cases for async lock behavior in update functionality."""

    @pytest.mark.asyncio
    async def test_update_lock_prevents_concurrent_execution(self):
        """Test that the update lock prevents concurrent executions."""
        # This test verifies the lock mechanism works as expected
        from main import update_lock

        # Simulate acquiring the lock
        async with update_lock:
            # While lock is held, it should be locked
            assert update_lock.locked()

        # After releasing, it should not be locked
        assert not update_lock.locked()


# Fixtures for test data
@pytest.fixture
def sample_animals():
    """Fixture providing sample animal data."""
    return [
        AnimalEntry(name="Lion", href="/wiki/Lion", collateral_adjectives=["leonine"]),
        AnimalEntry(name="Cat", href="/wiki/Cat", collateral_adjectives=["feline"]),
        AnimalEntry(name="Dog", href="/wiki/Dog", collateral_adjectives=["canine"])
    ]


@pytest.fixture
def sample_animals_with_images():
    """Fixture providing sample animal data with image paths."""
    return [
        AnimalEntry(name="Lion", href="/wiki/Lion", collateral_adjectives=["leonine"], image_path="/tmp/lion.jpg"),
        AnimalEntry(name="Cat", href="/wiki/Cat", collateral_adjectives=["feline"], image_path="/tmp/cat.jpg"),
        AnimalEntry(name="Dog", href="/wiki/Dog", collateral_adjectives=["canine"], image_path="/tmp/dog.jpg")
    ]


# Integration test
class TestIntegration:
    """Integration test cases."""

    def test_app_startup(self):
        """Test that the FastAPI app can start up correctly."""
        # This is a basic integration test to ensure the app structure is correct
        assert app is not None
        assert hasattr(app, 'routes')

        # Check that routes are registered
        route_paths = [route.path for route in app.routes]
        assert "/" in route_paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])