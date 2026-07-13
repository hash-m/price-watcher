import pytest
from unittest.mock import AsyncMock, MagicMock, patch
 
from bot.scraper import browser
 
 
@pytest.fixture(autouse=True)
def reset_singletons(monkeypatch):
    monkeypatch.setattr(browser, "PLAYWRIGHT_INSTANCE", None)
    monkeypatch.setattr(browser, "BROWSER_INSTANCE", None)
    monkeypatch.setattr(browser, "CONTEXT_INSTANCE", None)
 
 
class TestGetContext:
    @pytest.mark.asyncio
    async def test_creates_instances_on_first_call(self):
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
 
        mock_chromium = MagicMock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)
 
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium = mock_chromium
 
        mock_playwright_cm = MagicMock()
        mock_playwright_cm.start = AsyncMock(return_value=mock_playwright_instance)
 
        with patch.object(browser, "async_playwright", return_value=mock_playwright_cm):
            context = await browser.get_context()
 
        assert context is mock_context
        mock_chromium.launch.assert_awaited_once_with(headless=True)
        mock_browser.new_context.assert_awaited_once()
 
    @pytest.mark.asyncio
    async def test_reuses_existing_context_without_relaunching(self, monkeypatch):
        existing_context = AsyncMock()
        monkeypatch.setattr(browser, "CONTEXT_INSTANCE", existing_context)
 
        with patch.object(browser, "async_playwright") as mock_ap:
            context = await browser.get_context()
 
        assert context is existing_context
        mock_ap.assert_not_called()
 
 
class TestNewPage:
    @pytest.mark.asyncio
    async def test_returns_new_page_from_context(self, monkeypatch):
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
 
        monkeypatch.setattr(browser, "get_context", AsyncMock(return_value=mock_context))
 
        page = await browser.new_page()
 
        assert page is mock_page
        mock_context.new_page.assert_awaited_once()
 
 
class TestCloseBrowser:
    @pytest.mark.asyncio
    async def test_closes_all_instances_when_present(self, monkeypatch):
        mock_context = AsyncMock()
        mock_browser_inst = AsyncMock()
        mock_playwright_inst = AsyncMock()
 
        monkeypatch.setattr(browser, "CONTEXT_INSTANCE", mock_context)
        monkeypatch.setattr(browser, "BROWSER_INSTANCE", mock_browser_inst)
        monkeypatch.setattr(browser, "PLAYWRIGHT_INSTANCE", mock_playwright_inst)
 
        await browser.close_browser()
 
        mock_context.close.assert_awaited_once()
        mock_browser_inst.close.assert_awaited_once()
        mock_playwright_inst.stop.assert_awaited_once()
 
    @pytest.mark.asyncio
    async def test_no_error_when_nothing_was_initialised(self):
        await browser.close_browser()
