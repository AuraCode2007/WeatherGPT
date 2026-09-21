"""
tests/test_chat.py — WeatherGPT chat endpoint tests.
"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

_WEATHER_MOCK = {
    "city": "Delhi", "country": "IN", "temp": 36.0, "feels_like": 39.0,
    "temp_min": 33.0, "temp_max": 40.0, "condition": "Clear",
    "description": "Clear Sky", "humidity": 55, "wind_speed": 14.4,
    "wind_direction": 200, "visibility": 8.0, "uv_index": 8.0, "aqi": 2,
    "forecast": ["Mon 18 Sep: 35°C, Sunny, Humidity 55%"],
    "alert": None,
}


@patch("backend.routes.chat.fetch_weather", return_value=_WEATHER_MOCK)
@patch("backend.routes.chat.generate_weather_response", return_value="It is very hot and sunny today!")
@patch("backend.routes.chat.get_cached", return_value=None)
@patch("backend.routes.chat.set_cached")
def test_chat_live_response(mock_set, mock_get, mock_llm, mock_weather):
    resp = client.post("/chat/", json={
        "user_question": "How hot is it?",
        "location": "Delhi",
        "language_code": "en",
        "domain": "General",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"] == "It is very hot and sunny today!"
    assert data["source"] == "live"
    assert data["location"] == "Delhi"


@patch("backend.routes.chat.get_cached", return_value="Cached farmer advisory!")
def test_chat_returns_cached_response(mock_get):
    resp = client.post("/chat/", json={
        "user_question": "Should I irrigate my wheat?",
        "location": "Ludhiana",
        "language_code": "hi",
        "domain": "Agriculture / Farming",
    })
    assert resp.status_code == 200
    assert resp.json()["source"] == "cache"


@patch("backend.routes.chat.fetch_weather", side_effect=ValueError("City 'XYZ' not found."))
@patch("backend.routes.chat.get_cached", return_value=None)
def test_chat_404_for_unknown_city(mock_get, mock_weather):
    resp = client.post("/chat/", json={"user_question": "Weather?", "location": "XYZ"})
    assert resp.status_code == 404


def test_chat_missing_question():
    resp = client.post("/chat/", json={"location": "Delhi"})
    assert resp.status_code == 422   # Pydantic validation error
