"""tests for fetching, with a mocked http session and a patched pipeline"""

from unittest.mock import AsyncMock, patch

import pytest

import main
from weather_fetcher import build_params, fetch

pytestmark = pytest.mark.fetcher

LOCATION = {"name": "Białystok", "lat": 53.1333, "lon": 23.1643}
SOURCE = {
    "name": "weatherapi",
    "url": "https://api.weatherapi.com/v1/current.json",
    "api_key": "secret",
    "params": {"key": "{key}", "q": "{lat},{lon}", "aqi": "no"},
}


def test_build_params():
    assert build_params(SOURCE, LOCATION) == {
        "key": "secret",
        "q": "53.1333,23.1643",
        "aqi": "no",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("session_kwargs", "expected_data", "expected_error"),
    [
        pytest.param({"status": 200, "body": {"ok": 1}}, {"ok": 1}, None, id="ok"),
        pytest.param({"status": 401, "body": {"error": 1}}, None, "HTTP 401", id="401"),
        pytest.param({"raises": TimeoutError()}, None, "timeout", id="timeout"),
    ],
)
async def test_fetch_handles_responses(
    mock_session, session_kwargs, expected_data, expected_error
):
    session = mock_session(**session_kwargs)

    result = await fetch(session, SOURCE, LOCATION)

    assert result["data"] == expected_data
    assert result["error"] == expected_error
    assert result["elapsed_s"] is not None
    session.get.assert_called_once_with(
        SOURCE["url"], params=build_params(SOURCE, LOCATION), headers=None
    )


@pytest.mark.asyncio
async def test_main_runs_pipeline(sample_config, open_meteo_response):
    fetched = {
        "source": "open-meteo",
        "location": "Białystok",
        "data": open_meteo_response,
        "error": None,
        "elapsed_s": 0.1,
    }

    with (
        patch("main.load_config", return_value=sample_config),
        patch("main.fetch", new=AsyncMock(return_value=fetched)) as fake_fetch,
        patch("main.print_report") as fake_report,
    ):
        await main.main()

    fake_fetch.assert_awaited_once()
    readings, summary, results, _total_s = fake_report.call_args.args
    assert [r.source for r in readings] == ["open-meteo"]
    assert summary["Białystok"]["temp_c"]["mean"] == 6.8
    assert results == [fetched]
