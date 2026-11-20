"""shared fixtures for the test suite"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def sample_config() -> dict[str, Any]:
    """minimal valid config with one location and one keyless source"""
    return {
        "locations": [{"name": "Białystok", "lat": 53.1333, "lon": 23.1643}],
        "sources": [
            {
                "name": "open-meteo",
                "url": "https://api.open-meteo.com/v1/forecast",
                "params": {"latitude": "{lat}", "longitude": "{lon}"},
            }
        ],
    }


@pytest.fixture
def config_file(tmp_path: Path, sample_config: dict[str, Any]) -> Path:
    """sample_config written to a temporary config.json"""
    path = tmp_path / "config.json"
    path.write_text(json.dumps(sample_config, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def owm_response() -> dict[str, Any]:
    """trimmed real openweathermap response"""
    return {
        "weather": [{"id": 802, "main": "Clouds", "description": "scattered clouds"}],
        "main": {"temp": 280.03, "pressure": 985, "humidity": 97},
        "wind": {"speed": 2.24, "deg": 203},
    }


@pytest.fixture
def weatherapi_response() -> dict[str, Any]:
    """trimmed real weatherapi response"""
    return {
        "current": {
            "temp_c": 7.0,
            "condition": {"text": "Patchy rain nearby", "code": 1063},
            "wind_kph": 15.1,
            "pressure_mb": 986.0,
            "humidity": 93,
        }
    }


@pytest.fixture
def open_meteo_response() -> dict[str, Any]:
    """trimmed real open-meteo response"""
    return {
        "current": {
            "temperature_2m": 6.8,
            "relative_humidity_2m": 95,
            "pressure_msl": 985.8,
            "weather_code": 3,
            "wind_speed_10m": 2.4,
        }
    }


@pytest.fixture
def mock_session():
    """factory for a mocked aiohttp session returning a status or raising an error"""

    def make(status: int = 200, body: Any = None, raises: Exception | None = None):
        response = MagicMock(status=status)
        response.json = AsyncMock(return_value=body)
        response.text = AsyncMock(return_value=json.dumps(body))

        session = MagicMock()
        context = session.get.return_value
        if raises is not None:
            context.__aenter__.side_effect = raises
        else:
            context.__aenter__.return_value = response
        return session

    return make
