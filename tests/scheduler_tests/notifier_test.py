import pytest
from bot.scheduler.alerts_evaluator import check_alert


"""
!!!
    check_alert()
!!! vvvvvvvvvvvvv
"""
def make_alert(target, trigger, triggered):
    return (None, None, None, target, trigger, triggered)


def make_product(price=None, percentage=0, available=True):
    return {"FinalPrice": price, "Percentage": percentage, "Available": available}


class TestCheckAlertPrice:
    @pytest.mark.asyncio
    async def test_notify_when_at_trigger_and_not_triggered(self):
        result = await check_alert(make_alert("price", 100, False), make_product(price=100))
        assert result == "notify"

    @pytest.mark.asyncio
    async def test_notify_when_below_trigger(self):
        result = await check_alert(make_alert("price", 100, False), make_product(price=50))
        assert result == "notify"

    @pytest.mark.asyncio
    async def test_no_action_when_above_trigger_and_not_triggered(self):
        result = await check_alert(make_alert("price", 100, False), make_product(price=150))
        assert result == "dont"

    @pytest.mark.asyncio
    async def test_reset_when_above_trigger_and_was_triggered(self):
        result = await check_alert(make_alert("price", 100, True), make_product(price=150))
        assert result == "reset"

    @pytest.mark.asyncio
    async def test_no_action_when_at_trigger_and_already_triggered(self):
        result = await check_alert(make_alert("price", 100, True), make_product(price=100))
        assert result == "dont"

    @pytest.mark.asyncio
    async def test_price_as_none_returns_dont(self):
        result = await check_alert(make_alert("price", 100, False), make_product(price=None))
        assert result == "dont"


class TestCheckAlertPercentage:

    @pytest.mark.asyncio
    async def test_notify_when_at_or_above_trigger(self):
        result = await check_alert(make_alert("percentage", 20, False), make_product(percentage=20))
        assert result == "notify"

    @pytest.mark.asyncio
    async def test_notify_when_above_trigger(self):
        result = await check_alert(make_alert("percentage", 20, False), make_product(percentage=50))
        assert result == "notify"

    @pytest.mark.asyncio
    async def test_reset_when_below_trigger_and_was_triggered(self):
        result = await check_alert(make_alert("percentage", 20, True), make_product(percentage=10))
        assert result == "reset"

    @pytest.mark.asyncio
    async def test_no_discount_does_not_notify(self):
        result = await check_alert(make_alert("percentage", 20, False), make_product(percentage=0))
        assert result == "dont"

    @pytest.mark.asyncio
    async def test_price_increase_negative_percentage_does_not_notify(self):
        result = await check_alert(make_alert("percentage", 20, False), make_product(percentage=-900))
        assert result == "dont"

    @pytest.mark.asyncio
    async def test_percentage_as_none_returns_dont(self):
        result = await check_alert(make_alert("percentage", 10, False), make_product(percentage=None))
        assert result == "dont"


class TestCheckAlertAvailability:

    @pytest.mark.asyncio
    async def test_notify_when_matches_trigger_and_not_triggered(self):
        result = await check_alert(make_alert("availability", True, False), make_product(available=True))
        assert result == "notify"

    @pytest.mark.asyncio
    async def test_reset_when_differs_from_trigger_and_was_triggered(self):
        result = await check_alert(make_alert("availability", True, True), make_product(available=False))
        assert result == "reset"

    @pytest.mark.asyncio
    async def test_availability_as_none_returns_dont(self):
        result = await check_alert(make_alert("availability", True, False), make_product(available=None))
        assert result == "dont"

    @pytest.mark.asyncio
    async def test_no_action_when_matches_and_already_triggered(self):
        result = await check_alert(make_alert("availability", True, True), make_product(available=True))
        assert result == "dont"


class TestCheckAlertUnknownTarget:
    @pytest.mark.asyncio
    async def test_unknown_target_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown target"):
            await check_alert(make_alert("weight", 5, False), make_product())