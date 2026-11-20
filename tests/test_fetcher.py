"""testing weather fetcher on mock sources"""

import pytest

from weather_fetcher import build_params, fetch

LOCATION = {"name": "Białystok", "lat": 53.1333, "lon": 23.1643}


def test_build_params_fills_placeholders():
    source = {
        "name": "weatherapi",
        "api_key": "secret",
        "params": {"key": "{key}", "q": "{lat},{lon}", "aqi": "no"},
    }

    assert build_params(source, LOCATION) == {
        "key": "secret",
        "q": "53.1333,23.1643",
        "aqi": "no",
    }


class TimingOutSession:
    def get(self, *args, **kwargs):
        return self

    async def __aenter__(self):
        raise TimeoutError

    async def __aexit__(self, *exc):
        return False


@pytest.mark.asyncio
async def test_fetch_timeout_returns_error_instead_of_raising():
    source = {
        "name": "open-meteo",
        "url": "https://example.invalid",
        "params": {"latitude": "{lat}"},
    }

    result = await fetch(TimingOutSession(), source, LOCATION)

    assert result["data"] is None
    assert result["error"] == "timeout"
    assert result["elapsed_s"] is not None


class ErrorResponseSession:
    status = 401

    def get(self, *args, **kwargs):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def text(self):
        return '{"message": "Invalid API key"}'


@pytest.mark.asyncio
async def test_fetch_http_error_returns_error():
    source = {"name": "openweathermap", "url": "https://example.invalid", "params": {}}

    result = await fetch(ErrorResponseSession(), source, LOCATION)

    assert result["data"] is None
    assert result["error"] == "HTTP 401"
