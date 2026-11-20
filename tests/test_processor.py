"""tests for normalization and aggregation"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from data_processor import (
    NUMERIC_FIELDS,
    WeatherReading,
    aggregate,
    kelvin_to_celsius,
    normalize_all,
    normalize_open_meteo,
    normalize_owm,
    normalize_weatherapi,
)

pytestmark = pytest.mark.processor


@pytest.mark.parametrize(
    ("normalizer", "response_fixture", "expected"),
    [
        pytest.param(
            normalize_owm,
            "owm_response",
            WeatherReading(
                "openweathermap", "Białystok", 6.88, 97, 985, 2.24, "scattered clouds"
            ),
            id="openweathermap",
        ),
        pytest.param(
            normalize_weatherapi,
            "weatherapi_response",
            WeatherReading(
                "weatherapi", "Białystok", 7.0, 93, 986.0, 4.19, "Patchy rain nearby"
            ),
            id="weatherapi",
        ),
        pytest.param(
            normalize_open_meteo,
            "open_meteo_response",
            WeatherReading("open-meteo", "Białystok", 6.8, 95, 985.8, 2.4, None),
            id="open-meteo",
        ),
    ],
)
def test_normalizers(request, normalizer, response_fixture, expected):
    response = request.getfixturevalue(response_fixture)

    assert normalizer(response, "Białystok") == expected


def test_normalize_all_skips_bad_results(owm_response):
    results = [
        {
            "source": "openweathermap",
            "location": "A",
            "data": owm_response,
            "error": None,
        },
        {"source": "weatherapi", "location": "A", "data": None, "error": "HTTP 401"},
        {"source": "met-norway", "location": "A", "data": {}, "error": None},
        {
            "source": "openweathermap",
            "location": "B",
            "data": {"cod": 200},
            "error": None,
        },
    ]

    readings = normalize_all(results)

    assert [(r.source, r.location) for r in readings] == [("openweathermap", "A")]


@given(st.floats(min_value=-100, max_value=100))
def test_kelvin_roundtrip(celsius):
    assert kelvin_to_celsius(celsius + 273.15) == pytest.approx(celsius, abs=0.006)


optional_value = st.none() | st.floats(min_value=-100, max_value=1100)
readings_strategy = st.lists(
    st.builds(
        WeatherReading,
        source=st.sampled_from(["openweathermap", "weatherapi", "open-meteo"]),
        location=st.just("X"),
        temp_c=optional_value,
        humidity_pct=optional_value,
        pressure_hpa=optional_value,
        wind_ms=optional_value,
        description=st.none() | st.text(max_size=10),
    ),
    min_size=1,
    max_size=5,
)


@given(readings_strategy)
def test_aggregate_properties(readings):
    stats = aggregate(readings)["X"]

    for field in NUMERIC_FIELDS:
        values = [getattr(r, field) for r in readings if getattr(r, field) is not None]
        if not values:
            assert field not in stats
            continue

        s = stats[field]
        assert s["n"] == len(values)
        assert s["min"] == min(values)
        assert s["max"] == max(values)
        assert s["min"] - 0.005 <= s["mean"] <= s["max"] + 0.005
        assert s["spread"] >= 0
