"""
tests/test_simulation.py — Atmospheric AI Twin & Metrics tests.
"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


@patch("backend.routes.simulation.fetch_weather")
@patch("backend.routes.simulation.generate_simulation_analysis")
def test_simulation_endpoint(mock_ai_playbook, mock_fetch):
    mock_fetch.return_value = {
        "city": "Mumbai",
        "temp": 32.0,
        "feels_like": 36.0,
        "humidity": 70,
        "wind_speed": 15.0,
        "condition": "Partly Cloudy",
    }
    mock_ai_playbook.return_value = "### Tactical Playbook\nIssue heat advisories."

    payload = {
        "location": "Mumbai",
        "temp_delta": 5.0,
        "humidity_delta": 10.0,
        "rain_rate_mm_hr": 25.0,
        "wind_gust_kmh": 30.0,
        "domain": "Smart City / Urban",
        "preset_name": "Heat & Rain Surge"
    }
    response = client.post("/simulate/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Mumbai"
    assert data["simulated_weather"]["temp"] == 37.0
    assert "Agriculture" in data["impact_matrix"]
    assert "Aviation" in data["impact_matrix"]
    assert "Smart City" in data["impact_matrix"]
    assert "ai_playbook" in data


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "weathergpt_http_requests_total" in response.text
    assert "weathergpt_uptime_seconds" in response.text
