from weather_fetcher import build_params

LOCATION = {"name": "Białystok", "lat": 53.1333, "lon": 23.1643}


def test_build_params_fills_lat_lon_and_key():
    source = {
        "name": "openweathermap",
        "api_key": "secret",
        "params": {"lat": "{lat}", "lon": "{lon}", "appid": "{key}"},
    }

    assert build_params(source, LOCATION) == {
        "lat": "53.1333",
        "lon": "23.1643",
        "appid": "secret",
    }


def test_build_params_combined_placeholder():
    source = {"name": "weatherapi", "api_key": "k", "params": {"q": "{lat},{lon}", "aqi": "no"}}

    assert build_params(source, LOCATION) == {"q": "53.1333,23.1643", "aqi": "no"}


def test_build_params_without_api_key():
    source = {"name": "open-meteo", "params": {"latitude": "{lat}", "longitude": "{lon}"}}

    assert build_params(source, LOCATION) == {"latitude": "53.1333", "longitude": "23.1643"}
