from data_processor import (
    WeatherReading,
    aggregate,
    normalize_all,
    normalize_open_meteo,
    normalize_owm,
    normalize_weatherapi,
)

OWM_RESPONSE = {
    "weather": [{"id": 802, "main": "Clouds", "description": "scattered clouds"}],
    "main": {"temp": 280.03, "pressure": 985, "humidity": 97},
    "wind": {"speed": 2.24, "deg": 203},
}

WEATHERAPI_RESPONSE = {
    "current": {
        "temp_c": 7.0,
        "condition": {"text": "Patchy rain nearby", "code": 1063},
        "wind_kph": 15.1,
        "pressure_mb": 986.0,
        "humidity": 93,
    }
}

OPEN_METEO_RESPONSE = {
    "current": {
        "temperature_2m": 6.8,
        "relative_humidity_2m": 95,
        "pressure_msl": 985.8,
        "weather_code": 3,
        "wind_speed_10m": 2.4,
    }
}


def test_normalize_owm():
    assert normalize_owm(OWM_RESPONSE, "Białystok") == WeatherReading(
        source="openweathermap",
        location="Białystok",
        temp_c=6.88,
        humidity_pct=97,
        pressure_hpa=985,
        wind_ms=2.24,
        description="scattered clouds",
    )


def test_normalize_weatherapi():
    assert normalize_weatherapi(WEATHERAPI_RESPONSE, "Białystok") == WeatherReading(
        source="weatherapi",
        location="Białystok",
        temp_c=7.0,
        humidity_pct=93,
        pressure_hpa=986.0,
        wind_ms=4.19,
        description="Patchy rain nearby",
    )


def test_normalize_open_meteo():
    assert normalize_open_meteo(OPEN_METEO_RESPONSE, "Białystok") == WeatherReading(
        source="open-meteo",
        location="Białystok",
        temp_c=6.8,
        humidity_pct=95,
        pressure_hpa=985.8,
        wind_ms=2.4,
        description=None,
    )


def test_normalize_owm_tolerates_missing_fields():
    reading = normalize_owm({"main": {"temp": 280.0}, "weather": []}, "X")

    assert reading.temp_c == 6.85
    assert reading.humidity_pct is None
    assert reading.pressure_hpa is None
    assert reading.wind_ms is None
    assert reading.description is None


def test_normalize_all_skips_bad_results():
    results = [
        {
            "source": "openweathermap",
            "location": "Białystok",
            "data": OWM_RESPONSE,
            "error": None,
        },
        {
            "source": "weatherapi",
            "location": "Białystok",
            "data": None,
            "error": "HTTP 401",
        },
        {"source": "met-norway", "location": "Białystok", "data": {}, "error": None},
        {
            "source": "openweathermap",
            "location": "Warszawa",
            "data": {"cod": 200},
            "error": None,
        },
    ]

    readings = normalize_all(results)

    assert len(readings) == 1
    assert readings[0].source == "openweathermap"
    assert readings[0].location == "Białystok"


def test_aggregate_mean_spread_and_skips_none():
    readings = [
        WeatherReading(
            "openweathermap", "Białystok", 5.18, 93, 991, 1.79, "overcast clouds"
        ),
        WeatherReading("weatherapi", "Białystok", 5.2, 91, 992.0, None, "Overcast"),
        WeatherReading("open-meteo", "Białystok", 5.1, 96, 991.7, 2.8, None),
    ]

    summary = aggregate(readings)["Białystok"]

    assert summary["temp_c"] == {
        "mean": 5.16,
        "min": 5.1,
        "max": 5.2,
        "spread": 0.1,
        "n": 3,
    }
    assert summary["wind_ms"]["n"] == 2
    assert summary["descriptions"] == {
        "openweathermap": "overcast clouds",
        "weatherapi": "Overcast",
    }
