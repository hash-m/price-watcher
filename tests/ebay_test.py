import pytest

from unittest.mock     import AsyncMock
from bot.exceptions    import ExtractionError
from bot.scraper.sites import ebay


class TestExtract:
    def test_extracts_basic_fields(self):
        json_data = {
            "itemId": "v1|123|0",
            "title": "Test Item",
            "price": {"value": "19.99", "currency": "GBP"},
            "estimatedAvailabilities": [{"estimatedAvailabilityStatus": "IN_STOCK"}],
        }
        result = ebay.extract(json_data)
        assert result["Name"]       == "Test Item"
        assert result["FinalPrice"] == 19.99
        assert result["Available"]  == True

    def test_out_of_stock_item(self):
        json_data = {
            "itemId": "v1|123|0",
            "title": "Test Item",
            "price": {"value": "19.99"},
            "estimatedAvailabilities": [{"estimatedAvailabilityStatus": "OUT_OF_STOCK"}],
        }
        result = ebay.extract(json_data)
        assert result["Available"] == False

    def test_missing_availabilities_defaults_to_unavailable(self):
        json_data = {
            "itemId": "v1|123|0",
            "title": "Test Item",
            "price": {"value": "19.99"},
        }
        result = ebay.extract(json_data)
        assert result["Available"] == False

    def test_missing_itemid_raises_extraction_error(self):
        with pytest.raises(ExtractionError):
            ebay.extract({"title": "no id"})

    def test_empty_json_raises_extraction_error(self):
        with pytest.raises(ExtractionError):
            ebay.extract({})

    def test_none_json_raises_extraction_error(self):
        with pytest.raises(ExtractionError):
            ebay.extract(None)

class TestExtract:
    def test_extracts_basic_fields(self):
        json_data = {
            "itemId": "v1|123|0",
            "title": "Test Item",
            "price": {"value": "19.99"},
            "estimatedAvailabilities": [{"estimatedAvailabilityStatus": "IN_STOCK"}],
        }
        result = ebay.extract(json_data)
        assert result["Name"] == "Test Item"
        assert result["FinalPrice"] == 19.99
        assert result["Available"] is True
 
    def test_missing_itemid_raises_extraction_error(self):
        with pytest.raises(ExtractionError):
            ebay.extract({"title": "no id"})
 
 
def build_fake_fetch_json():
    def compute_response(url,hearders={}):
        # url looks like: https://api.ebay.com/buy/browse/v1/item/v1|<id>|0
        embedded_id = url.split("|")[1]
        return {
            "itemId": f"v1|{embedded_id}|0",
            "title": "Widget",
            "price": {"value": "9.99"},
        }
 
    return AsyncMock(side_effect=compute_response)


class TestFetch:
    def test_get_itemid_succeeding(self):
        result = ebay.get_itemid('https://www.ebay.co.uk/itm/298307755049?misc')
        assert result == 298307755049

    
    @pytest.mark.asyncio
    async def test_fetch_returns_response_with_correct_itemId(self,monkeypatch):
        fake_fetch_json = build_fake_fetch_json()
        monkeypatch.setattr(ebay, "fetch_json", fake_fetch_json)
 
        url = "https://www.ebay.co.uk/itm/234567891234"
        result = await ebay.fetch(url)
 

        assert result["itemId"] == "v1|234567891234|0"

