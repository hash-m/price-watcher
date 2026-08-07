import pytest

from unittest.mock     import patch
from bot.exceptions    import ExtractionError, FetchingError
from bot.scraper.sites import ebay


"""
!!!
    get_itemid()
!!! vvvvvvvvvvvv
"""
def test_get_itemid_succeeding():
    result = ebay.get_itemid('https://www.ebay.co.uk/itm/298307755049?misc')
    assert result == 298307755049
 
def test_get_itemid_non_string_input():
    assert ebay.get_itemid(12345) is None
    assert ebay.get_itemid(None) is None

def test_get_itemid_no_second_path_segment():
    assert ebay.get_itemid('https://www.ebay.co.uk/itm') is None

def test_get_itemid_trailing_slash_only():
    assert ebay.get_itemid('https://www.ebay.co.uk/') is None

def test_get_itemid_non_numeric_id():
    assert ebay.get_itemid('https://www.ebay.co.uk/itm/abc?misc') is None

def test_get_itemid_empty_string():
    assert ebay.get_itemid('') is None


"""
!!!
    extract()
!!! vvvvvvvvvvvv
"""

@pytest.mark.asyncio
async def test_extracts_basic_fields():
    json_data = {
        "itemId": "v1|123|0",
        "title": "Test Item",
        "price": {"value": "19.99", "currency": "GBP"},
        "estimatedAvailabilities": [{"estimatedAvailabilityStatus": "IN_STOCK"}],
    }
    result = await ebay.extract(json_data)
    assert result["Name"] == "Test Item"
    assert result["FinalPrice"] == 19.99
    assert result["Available"] is True
    assert result["InitialPrice"] is None

@pytest.mark.asyncio
async def test_out_of_stock_item():
    json_data = {
        "itemId": "v1|123|0",
        "title": "Test Item",
        "price": {"value": "19.99"},
        "estimatedAvailabilities": [{"estimatedAvailabilityStatus": "OUT_OF_STOCK"}],
    }
    result = await ebay.extract(json_data)
    assert result["Available"] is False

@pytest.mark.asyncio
async def test_missing_availabilities_key_defaults_to_unavailable():
    json_data = {"itemId": "v1|123|0", "title": "Test Item", "price": {"value": "19.99"}}
    result = await ebay.extract(json_data)
    assert result["Available"] is False

@pytest.mark.asyncio
async def test_empty_availabilities_list_defaults_to_unavailable():
    json_data = {
        "itemId": "v1|123|0",
        "title": "Test Item",
        "price": {"value": "19.99"},
        "estimatedAvailabilities": [],
    }
    result = await ebay.extract(json_data)
    assert result["Available"] is False

@pytest.mark.asyncio
async def test_price_present_but_value_missing_causing_extraction_error():
    json_data = {"itemId": "v1|123|0", "title": "Test Item", "price": {}}
    with pytest.raises(ExtractionError):
        await ebay.extract(json_data)
        

@pytest.mark.asyncio
async def test_missing_itemid_raises_extraction_error():
    with pytest.raises(ExtractionError):
        await ebay.extract({"title": "no id"})

@pytest.mark.asyncio
async def test_empty_json_raises_extraction_error():
    with pytest.raises(ExtractionError):
        await ebay.extract({})

@pytest.mark.asyncio
async def test_none_json_raises_extraction_error():
    with pytest.raises(ExtractionError):
        await ebay.extract(None)

@pytest.mark.asyncio
async def test_missing_price_key_raises_extraction_error():
    json_data = {"itemId": "v1|123|0", "title": "Test Item"}
    with pytest.raises(ExtractionError):
        await ebay.extract(json_data)


"""
!!!
    fetch()
!!!
"""

@pytest.mark.asyncio
async def test_fetching_error_raised_when_itemid_is_missing():
    with patch("bot.scraper.fetcher.fetch_json", side_effect="Shouldn't be called"):
        with pytest.raises(FetchingError):
            await ebay.fetch("ho")
