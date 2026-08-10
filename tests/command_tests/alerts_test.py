import pytest
from unittest.mock import patch, AsyncMock
from bot.logic import alerts as a
 
 
class TestAddAlertValidation:
 
    @pytest.mark.asyncio
    async def test_raises_on_unknown_target(self):
        with pytest.raises(ValueError):
            await a.add_alert("https://diy.com/1", 1, "weight", 50)
 
    @pytest.mark.asyncio
    async def test_raises_on_negative_price_trigger(self):
        with pytest.raises(ValueError):
            await a.add_alert("https://diy.com/1", 1, "price", -1)
 
    @pytest.mark.asyncio
    async def test_raises_on_percentage_trigger_below_one(self):
        with pytest.raises(ValueError):
            await a.add_alert("https://diy.com/1", 1, "percentage", 0)
 
    @pytest.mark.asyncio
    async def test_raises_on_percentage_trigger_above_hundred(self):
        with pytest.raises(ValueError):
            await a.add_alert("https://diy.com/1", 1, "percentage", 101)
 
    @pytest.mark.asyncio
    async def test_allows_zero_price_trigger(self):
        with patch.object(a, "alert_exists", new=AsyncMock(return_value=False)), patch.object(a, "add_alert_to_db", new=AsyncMock()):
            result = await a.add_alert("https://diy.com/1", 1, "price", 0)
            assert result == "Added Alert"
 
    @pytest.mark.asyncio
    async def test_allows_percentage_trigger_at_lower_boundary(self):
        with patch.object(a, "alert_exists", new=AsyncMock(return_value=False)), patch.object(a, "add_alert_to_db", new=AsyncMock()):
            result = await a.add_alert("https://diy.com/1", 1, "percentage", 1)
            assert result == "Added Alert"
 
    @pytest.mark.asyncio
    async def test_allows_percentage_trigger_at_upper_boundary(self):
        with patch.object(a, "alert_exists", new=AsyncMock(return_value=False)), patch.object(a, "add_alert_to_db", new=AsyncMock()):
            result = await a.add_alert("https://diy.com/1", 1, "percentage", 100)
            assert result == "Added Alert"
 