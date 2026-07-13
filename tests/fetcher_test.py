import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.scraper import fetcher


class TestFetchJson:
    @pytest.mark.asyncio
    async def test_returns_parsed_json_body(self):
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"key": "value"})

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_cm.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_get_cm)

        mock_session_cm = MagicMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock(return_value=False)

        with patch.object(fetcher.aiohttp, "ClientSession", return_value=mock_session_cm):
            result = await fetcher.fetch_json("https://example.com/api")

        assert result == {"key": "value"}
        mock_session.get.assert_called_once_with("https://example.com/api")


class TestFetchPlaywright:
    @pytest.mark.asyncio
    async def test_navigates_and_returns_rendered_content(self, monkeypatch):
        mock_page = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>rendered</html>")

        monkeypatch.setattr(fetcher, "new_page", AsyncMock(return_value=mock_page))

        result = await fetcher.fetch_playwright("https://example.com")

        mock_page.goto.assert_awaited_once_with("https://example.com", wait_until="domcontentloaded")
        mock_page.wait_for_timeout.assert_awaited_once_with(5000)
        mock_page.close.assert_awaited_once()
        assert result == "<html>rendered</html>"