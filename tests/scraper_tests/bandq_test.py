import pytest
from unittest.mock import AsyncMock
from bs4 import BeautifulSoup

from bot.scraper.sites import bandq


HTML_DISCOUNTED = """
<html><body>
<table><tr><th>Product code</th><td>ABC123</td></tr></table>
<div data-testid="product-name">Cordless Drill</div>
<div data-testid="product-price">£45.00</div>
<div data-testid="was-price"><s>£60.00</s></div>
</body></html>
"""

HTML_NO_DISCOUNT = """
<html><body>
<table><tr><th>Product code</th><td>ABC123</td></tr></table>
<div data-testid="product-name">Cordless Drill</div>
<div data-testid="product-price">£45.00</div>
</body></html>
"""

HTML_NO_PRODUCT_CODE = "<html><body><table></table></body></html>"

FULFILMENT_AVAILABLE = {
    "data": [{"attributes": {"store_1": {"availability": "Available"}}}]
}

FULFILMENT_UNAVAILABLE = {
    "data": [{"attributes": {"store_1": {"availability": "Out of stock"}}}]
}


class TestGetProductCode:
    def test_finds_product_code(self):
        soup = BeautifulSoup(HTML_DISCOUNTED, "html.parser")
        assert bandq.get_productcode(soup) == "ABC123"

    def test_missing_product_code_returns_nothing(self):
        soup = BeautifulSoup(HTML_NO_PRODUCT_CODE, "html.parser")
        product_code = bandq.get_productcode(soup)
        assert product_code == None


class TestExtract:
    @pytest.mark.asyncio
    async def test_extracts_discounted_product(self, monkeypatch):
        monkeypatch.setattr(bandq, "fetch_json", AsyncMock(return_value=FULFILMENT_AVAILABLE))

        result = await bandq.extract(HTML_DISCOUNTED)

        assert result["Name"] == "Cordless Drill"
        assert result["InitialPrice"] == "£60.00"
        assert result["FinalPrice"]   == "£45.00"
        assert result["Available"]    == True

    @pytest.mark.asyncio
    async def test_extracts_non_discounted_product(self, monkeypatch):
        monkeypatch.setattr(bandq, "fetch_json", AsyncMock(return_value=FULFILMENT_AVAILABLE))

        result = await bandq.extract(HTML_NO_DISCOUNT)

        assert result["InitialPrice"] == None
        assert result["FinalPrice"]   == "£45.00"

    @pytest.mark.asyncio
    async def test_marks_unavailable_when_no_store_has_stock(self, monkeypatch):
        monkeypatch.setattr(bandq, "fetch_json", AsyncMock(return_value=FULFILMENT_UNAVAILABLE))

        result = await bandq.extract(HTML_DISCOUNTED)

        assert result["Available"] == False

    @pytest.mark.asyncio
    async def test_calls_fetch_json_with_correct_product_code(self, monkeypatch):
        fake_fetch_json = AsyncMock(return_value=FULFILMENT_AVAILABLE)
        monkeypatch.setattr(bandq, "fetch_json", fake_fetch_json)

        await bandq.extract(HTML_DISCOUNTED)

        fake_fetch_json.assert_awaited_once_with(
            "https://www.diy.com/browse-mfe/api/fulfilment-options?compositeOfferId=ABC123"
        )