import pytest
import bot.scraper.parser as parser

from unittest.mock import patch, AsyncMock



"""
!!!
    calculate_percentage()
!!! vvvvvvvvvvvvvvvvvvvvvv
"""
@pytest.mark.parametrize("initial,final", [
    (None,1000),
    (1000,None),
    (0,10000),
])
def test_invalid_params_in_percentage_calculation(initial,final):
    assert parser.calculate_percentage(initial,final) == 0

def test_100_percent_off():
    assert parser.calculate_percentage(100,0) == 100

def test_0_percent_off():
    assert parser.calculate_percentage(100,100) == 0

def test_price_increase_in_percentage():
    assert parser.calculate_percentage(100,1000) == -900


"""
!!!
    format_percentage()
!!! vvvvvvvvvvvvvvvvvvv
"""

def test_no_percentage_to_format():
    assert parser.format_percentage(None) == 0.0

@pytest.mark.parametrize("percentage,expected_result", [
    (-900,-900),
    (-50,-50),
    ("-900%",-900),
    (-0,0),
    ("-0",0)
])
def test_negative_percentage_can_be_formatted(percentage,expected_result):
    assert parser.format_percentage(percentage) == expected_result

@pytest.mark.parametrize("percentage,expected_result", [
    ("  900%",900),
    ("50%  ",50),
    ("  900 %  ",900)
])
def test_whitespace_in_percentage_format(percentage,expected_result):
    assert parser.format_percentage(percentage) == expected_result

def test_percentage_sign_only_in_perentage_format():
    assert parser.format_percentage("%") == 0

@pytest.mark.parametrize("percentage,expected_result", [
    ("1,000%",1000), #very unlikely but who knows with these pc hardware price increases
    ("100,000%",100000),
    ("1,000,000%",1000000)
])
def test_comma_separator_removed_in_percentage_format(percentage,expected_result):
    assert parser.format_percentage(percentage) == expected_result

@pytest.mark.parametrize("initial,final,expected", [
    (9.99, 6.99, 30.03),
    (19.99, 14.99, 25.01),
    (33, 11, 66.67),
])
def test_calculate_percentage_rounds_prices(initial, final, expected):
    assert parser.calculate_percentage(initial, final) == expected


"""
!!!
    format_price()
!!! vvvvvvvvvvvvvv
"""

def test_no_price_returns_nothing_from_format():
    assert parser.format_price(None) is None

@pytest.mark.parametrize("price,expected_result", [
    ("£100  ",100),
    ("  $100000",100000),
    ("  £ 1000000  ",1000000),
    ("$1,000",1000),
    ("£100,000",100000),
    ("1,000,000",1000000),
    ("1,000.59",1000.59)
])
def test_price_formatting_with_strings(price,expected_result):
    assert parser.format_price(price) == expected_result

@pytest.mark.parametrize("price,expected_result", [
    ("100.591",100.59),
    ("0.00000000002",0.00),
    ("0.005",0.01),
    ("99.999",100)
])
def test_rounding_in_price_formatting(price,expected_result):
    assert parser.format_price(price) == expected_result

"""
!!!
    format()
!!! vvvvvvvv
"""

@pytest.mark.asyncio
async def test_format_formats_final_price():
    raw = {"URL": "https://diy.com/1", "FinalPrice": "£50", "InitialPrice": "£100"}
    result = await parser.format(raw)
    assert result["FinalPrice"] == 50.0
 
 
@pytest.mark.asyncio
async def test_format_leaves_final_price_absent_if_not_provided():
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100"}
    result = await parser.format(raw)
    assert "FinalPrice" not in result

 
@pytest.mark.asyncio
async def test_format_formats_initial_price_when_provided():
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100", "FinalPrice": "£50"}
    with patch("bot.scraper.parser.get_init", new=AsyncMock()) as mock_get_init:
        result = await parser.format(raw)
 
    mock_get_init.assert_not_called()
    assert result["InitialPrice"] == 100.0
 
 
@pytest.mark.asyncio
async def test_format_looks_up_initial_price_when_missing():
    raw = {"URL": "https://diy.com/1", "FinalPrice": "£50"}
    with patch("bot.scraper.parser.get_init", new=AsyncMock(return_value=100)) as mock_get_init:
        result = await parser.format(raw)
 
    mock_get_init.assert_awaited_once_with("https://diy.com/1")
    assert result["InitialPrice"] == 100.0
 
 
@pytest.mark.asyncio
async def test_format_handles_get_init_returning_none():
    # product not in DB yet - get_init returns None
    raw = {"URL": "https://diy.com/1", "FinalPrice": "£50"}
    with patch("bot.scraper.parser.get_init", new=AsyncMock(return_value=None)):
        result = await parser.format(raw)
 
    assert result["InitialPrice"] is None
    # Percentage should safely default via calculate_percentage's None check
    assert result["Percentage"] == 0
 
 
@pytest.mark.asyncio
async def test_format_uses_explicit_percentage_without_recalculating():
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100", "FinalPrice": "£50", "Percentage": "30%"}
    result = await parser.format(raw)
    assert result["Percentage"] == 30.0
 
 
@pytest.mark.asyncio
async def test_format_calculates_percentage_when_both_prices_present():
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100", "FinalPrice": "£50"}
    result = await parser.format(raw)
    assert result["Percentage"] == 50.0
 
 
@pytest.mark.asyncio
async def test_format_defaults_percentage_to_zero_when_final_price_missing():
    # no FinalPrice key at all, no Percentage key so it hits the else branch
    raw = {"URL": "https://diy.com/1"}
    with patch("bot.scraper.parser.get_init", new=AsyncMock(return_value=None)):
        result = await parser.format(raw)
    assert result["Percentage"] == 0
 
 
@pytest.mark.asyncio
async def test_format_calculates_percentage_even_when_final_price_is_none():
    # FinalPrice key present but unparseable; InitialPrice always present
    # by this point, so elif triggers and calculate_percentage handles the None safely
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100", "FinalPrice": None}
    result = await parser.format(raw)
    assert result["Percentage"] == 0
    assert result["FinalPrice"] is None

 
@pytest.mark.asyncio
async def test_format_preserves_url_and_other_keys():
    raw = {"URL": "https://diy.com/1", "InitialPrice": "£100", "FinalPrice": "£50", "Name": "Drill"}
    result = await parser.format(raw)
    assert result["URL"] == "https://diy.com/1"
    assert result["Name"] == "Drill"
