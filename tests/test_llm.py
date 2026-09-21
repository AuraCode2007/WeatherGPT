"""
tests/test_llm.py — WeatherGPT LLM service tests.
"""
from unittest.mock import patch, MagicMock
import pytest
from backend.services.llm_service import generate_weather_response, generate_climate_summary, translate_text

_WEATHER = {
    "temp": 36, "feels_like": 39, "temp_min": 33, "temp_max": 40,
    "condition": "Clear", "description": "Clear Sky",
    "humidity": 55, "wind_speed": 14.4, "wind_direction": 200,
    "visibility": 8.0, "uv_index": 8.0, "aqi": 2,
    "forecast": ["Mon 18 Sep: 35°C, Sunny, Humidity 52%"],
    "alert": None,
}


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_generate_weather_response_english(mock_client, mock_get_client):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = MagicMock(text="  It is hot and sunny.  ")
    mock_client.chats.create.return_value = mock_chat
    mock_get_client.return_value = mock_client
    result = generate_weather_response("How hot?", "Delhi", _WEATHER, "en", "General")
    assert result == "It is hot and sunny."


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_generate_weather_response_hindi(mock_client, mock_get_client):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = MagicMock(text="आज बहुत गर्मी है।")
    mock_client.chats.create.return_value = mock_chat
    mock_get_client.return_value = mock_client
    result = generate_weather_response("आज मौसम कैसा है?", "Delhi", _WEATHER, "hi", "Agriculture / Farming")
    assert "गर्मी" in result


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_generate_weather_response_domain_aviation(mock_client, mock_get_client):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = MagicMock(text="Visibility is 8 km, winds at 200° — VFR conditions.")
    mock_client.chats.create.return_value = mock_chat
    mock_get_client.return_value = mock_client
    result = generate_weather_response("Safe to fly?", "Delhi", _WEATHER, "en", "Aviation")
    assert "VFR" in result or "km" in result


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_generate_climate_summary(mock_client, mock_get_client):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = MagicMock(text="July is hot and humid in Delhi.")
    mock_client.chats.create.return_value = mock_chat
    mock_get_client.return_value = mock_client
    clim = {"avg_temp": 34.0, "avg_humidity": 78.0, "avg_rainfall_mm": 180.0}
    result = generate_climate_summary("Delhi", 7, clim)
    assert len(result) > 0


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_generate_response_fallback_on_api_error(mock_client, mock_get_client):
    mock_client.chats.create.side_effect = Exception("Quota exceeded")
    mock_get_client.return_value = mock_client
    result = generate_weather_response("Is it rainy?", "Mumbai", _WEATHER)
    assert "WeatherGPT Intelligence Briefing" in result or "Mumbai" in result


@patch("backend.services.llm_service._get_client")
@patch("backend.services.llm_service._client")
def test_translate_text_english_passthrough(mock_client, mock_get_client):
    mock_get_client.return_value = mock_client
    result = translate_text("Hello world", "en")
    assert result == "Hello world"
    mock_client.chats.create.assert_not_called()



