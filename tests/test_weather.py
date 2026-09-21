"""
tests/test_weather.py — WeatherGPT weather service tests.
"""
from unittest.mock import patch, MagicMock
import pytest
from backend.services.weather_service import fetch_weather


def _geo_mock():
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = [{"lat": 28.6, "lon": 77.2, "name": "Delhi", "country": "IN"}]
    return m


def _current_mock():
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = {
        "name": "Delhi",
        "main": {"temp": 36.0, "feels_like": 39.0, "temp_min": 33.0, "temp_max": 40.0, "humidity": 55},
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "wind": {"speed": 4.0, "deg": 200},
        "visibility": 8000,
    }
    return m


def _forecast_mock():
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = {"list": [
        {"dt_txt": "2026-09-19 12:00:00", "main": {"temp": 35, "humidity": 52},
         "weather": [{"description": "sunny"}]},
        {"dt_txt": "2026-09-20 12:00:00", "main": {"temp": 34, "humidity": 50},
         "weather": [{"description": "clear sky"}]},
    ]}
    return m


def _aqi_mock():
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = {"list": [{"main": {"aqi": 2}}]}
    return m


@patch("backend.services.weather_service.requests.get")
def test_fetch_weather_returns_all_fields(mock_get):
    mock_get.side_effect = [_geo_mock(), _current_mock(), _forecast_mock(), _aqi_mock()]
    data = fetch_weather("Delhi")
    assert data["city"] == "Delhi"
    assert data["temp"] == 36.0
    assert data["humidity"] == 55
    assert data["aqi"] == 2
    assert isinstance(data["forecast"], list)
    assert len(data["forecast"]) <= 5


@patch("backend.services.weather_service.requests.get")
def test_fetch_weather_raises_for_unknown_city(mock_get):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = []          # empty geo response = city not found
    mock_get.return_value = m
    with pytest.raises(ValueError, match="not found"):
        fetch_weather("UnknownCityXYZ")


@patch("backend.services.weather_service.requests.get")
def test_extreme_heat_alert_generated(mock_get):
    """Temperatures >= 42°C should trigger a RED ALERT."""
    geo = _geo_mock()
    cur = MagicMock()
    cur.status_code = 200
    cur.json.return_value = {
        "name": "Bikaner",
        "main": {"temp": 44.0, "feels_like": 48.0, "temp_min": 40.0, "temp_max": 46.0, "humidity": 20},
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "wind": {"speed": 3.0, "deg": 180},
        "visibility": 10000,
    }
    mock_get.side_effect = [geo, cur, _forecast_mock(), _aqi_mock()]
    data = fetch_weather("Bikaner")
    assert data["alert"] is not None
    assert "RED ALERT" in data["alert"] or "Heat Wave" in data["alert"]
