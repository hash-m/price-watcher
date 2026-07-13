import pytest
from unittest.mock import AsyncMock, patch

from bot.exceptions import ExtractionError,FetchingError
from bot.scraper.sites import steam


class TestGetGameId:
    def test_string_url_extracts_id_segment(self):
        url = "https://store.steampowered.com/app/440/Team_Fortress_2/"
        assert steam.get_gameid(url) == 440

    def test_string_url_without_trailing_slash(self):
        url = "https://store.steampowered.com/app/570/Dota_2"
        assert steam.get_gameid(url) == 570

    def test_non_dict_non_str_input_returns_none(self):
        assert steam.get_gameid(12345) == None

    def test_bad_url(self):
        url = "https://store.steampowered.com/hardware/steammachine"
        assert steam.get_gameid(url) == None


class TestExtract:
    def test_extracts_basic_fields(self):
        payload = {
            "440": {
                "success": True,
                "data": {
                    "name": "Team Fortress 2",
                    "release_date": {"coming_soon": False},
                    "price_overview": {
                        "initial_formatted": "£10.99",
                        "final_formatted": "£5.49",
                        "discount_percent": 50,
                    },
                    "is_free": False,
                },
            }
        }
        result = steam.extract(payload)
        assert result["Name"] == "Team Fortress 2"
        assert result["Available"]    == True
        assert result["InitialPrice"] == "£10.99"
        assert result["FinalPrice"]   == "£5.49"
        assert result["Percentage"]   == 50

    def test_coming_soon_marks_unavailable(self):
        payload = {
            "440": {
                "success": True,
                "data": {
                    "name": "Unreleased Game",
                    "release_date": {"coming_soon": True},
                },
            }
        }
        result = steam.extract(payload)
        assert result["Available"] is False

    def test_free_game_overrides_prices_to_zero(self):
        payload = {
            "440": {
                "success": True,
                "data": {
                    "name": "Free Game",
                    "is_free": True,
                },
            }
        }
        result = steam.extract(payload)
        assert result["InitialPrice"] == 0
        assert result["FinalPrice"] == 0
        assert result["Percentage"] == 0

    def test_no_price_overview_and_not_free_omits_price_fields(self):
        payload = {
            "440": {
                "success": True,
                "data": {"name": "No price info"},
            }
        }
        result = steam.extract(payload)
        assert "InitialPrice" not in result
        assert "FinalPrice" not in result

    def test_raises_extraction_error_when_success_false(self):
        payload = {"440": {"success": False}}
        with pytest.raises(ExtractionError):
            steam.extract(payload)

    def test_raises_extraction_error_when_game_missing(self):
        payload = {}
        with pytest.raises(ExtractionError):
            steam.extract(payload)


class TestFetch:
    @pytest.mark.asyncio
    async def test_fetch_calls_appdetails_api_with_gameid(self):
        fake_json = {"440": {"success": True}}
        with patch.object(steam, "fetch_json", AsyncMock(return_value=fake_json)) as fetch_mock:
            result = await steam.fetch("https://store.steampowered.com/app/440/Team_Fortress_2/")

        fetch_mock.assert_awaited_once_with(
            "https://store.steampowered.com/api/appdetails?appids=440&cc=gb"
        )
        assert result == fake_json

    @pytest.mark.asyncio
    async def test_fetch_stops_on_missing_gameid(self, monkeypatch):
        fake_fetch_json = AsyncMock(return_value={})
        monkeypatch.setattr(steam, "fetch_json", fake_fetch_json)
        monkeypatch.setattr(steam, "get_gameid", lambda data: None)

        with pytest.raises(FetchingError):
            await steam.fetch("not-a-steam-url")

        
        fake_fetch_json.assert_not_awaited()
