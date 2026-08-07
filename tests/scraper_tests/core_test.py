import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from bot.scraper.core import get_functions,SCRAPER_MAPPING,scrape
from bot.exceptions import ScrapeError


""" 
!!!
    get_functions() test
!!! vvvvvvvvvvvvvvvvvvvv
""" 

@pytest.mark.parametrize("url,expected_domain", [
    ("https://diy.com/some/path", "diy.com"),
    ("https://www.diy.com/some/path", "diy.com"),
    ("http://www.ebay.co.uk/itm/12345", "ebay.co.uk"),
    ("https://store.steampowered.com/app/123", "store.steampowered.com"),
])
def test_matches_known_domains(url, expected_domain):
    assert get_functions(url) == SCRAPER_MAPPING[expected_domain]


def test_unknown_domain_returns_none():
    assert get_functions("https://unknown-site.com/page") is None



@pytest.mark.parametrize("url,expected_domain", [
    ("diy.com/some/path", "diy.com"),
    ("www.diy.com/some/path", "diy.com"),
    ("ebay.co.uk/itm/12345", "ebay.co.uk"),
])
def test_different_url_still_matches(url, expected_domain):
    assert get_functions(url) == SCRAPER_MAPPING[expected_domain]


@pytest.mark.parametrize("url,expected_domain", [
    ("https://DIY.com/some/path", "diy.com"),
    ("https://Store.SteamPowered.com/app/123", "store.steampowered.com"),
    ("EBAY.CO.UK/itm/1", "ebay.co.uk"),
])
def test_case_insensitive_matching(url, expected_domain):
    assert get_functions(url) == SCRAPER_MAPPING[expected_domain]


def test_strips_surrounding_whitespace():
    assert get_functions("  https://diy.com/some/path  ") == SCRAPER_MAPPING["diy.com"]



@pytest.mark.parametrize("url", [
    "https://uk.ebay.co.uk/itm/1",
    "https://m.ebay.co.uk/itm/1",
    "https://shop.diy.com/some/path",
])
def test_subdomains_return_none(url):
    assert get_functions(url) is None

"""
!!!
    scrape() test
!!! vvvvvvvvvvvvv
"""

@pytest.mark.asyncio
async def test_scrape_raises_for_unsupported_site():
    with patch("bot.scraper.core.get_functions", return_value=None):
        with pytest.raises(ValueError, match="Unsupported website"):
            await scrape("uk.ebay.co.uk/itm/1")



@pytest.mark.asyncio
async def test_scrape_raises_when_fetch_missing():
    functions = {"fetch": None, "extract": MagicMock()}
    with patch("bot.scraper.core.get_functions", return_value=functions):
        with pytest.raises(ScrapeError, match="fetch"):
            await scrape("www.diy.com/123")


@pytest.mark.asyncio
async def test_scrape_raises_when_extract_missing():
    functions = {"fetch": AsyncMock(), "extract": None}
    with patch("bot.scraper.core.get_functions", return_value=functions):
        with pytest.raises(ScrapeError, match="extract"):
            await scrape("www.diy.com/123")


@pytest.mark.asyncio
async def test_scrape_raises_when_both_missing():
    functions = {"fetch": None, "extract": None}
    with patch("bot.scraper.core.get_functions", return_value=functions):
        with pytest.raises(ScrapeError, match="fetch and extract"):
            await scrape("www.diy.com/123")


@pytest.mark.asyncio
@patch("bot.scraper.core.get_functions")
@patch("bot.scraper.core.format")
async def test_async_extract_is_awaited(mock_format,mock_functions):
    fake_fetch = AsyncMock(return_value="html")
    fake_extract = AsyncMock(return_value={"title" : "product"})
    mock_functions_result = {"fetch" : fake_fetch, "extract" : fake_extract}
    mock_functions.return_value = mock_functions_result
    mock_format.return_value = fake_extract.return_value
    
    result = await scrape("www.diy.com/123")

    fake_extract.assert_awaited_once_with("html")
    assert result["URL"] == "www.diy.com/123"

@pytest.mark.asyncio
@patch("bot.scraper.core.get_functions")
@patch("bot.scraper.core.format")
async def test_sync_extract_is_called(mock_format,mock_functions):
    fake_fetch = AsyncMock(return_value="html")
    fake_extract = MagicMock(return_value={"title": "product"})
    mock_functions_result = {"fetch" : fake_fetch, "extract" : fake_extract}
    mock_functions.return_value = mock_functions_result
    mock_format.return_value = fake_extract.return_value

    result = await scrape("www.diy.com/123")

    fake_extract.assert_called_once_with("html")
    assert result["URL"] == "www.diy.com/123"