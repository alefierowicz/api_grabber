"""normalization and aggregation of weather data from multiple sources"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class WeatherReading:
    """one reading from one source for one location, in common units"""
    source: str
    location: str
    temp_c: float | None
    humidity_pct: float | None
    pressure_hpa: float | None
    wind_ms: float | None
    description: str | None
    elapsed_s: float | None = None


def kelvin_to_celsius(k: float) -> float:
    """convert kelvin to degrees celsius"""
    return round(k - 273.15, 2)


def kph_to_ms(kph: float) -> float:
    """convert km/h to m/s"""
    return round(kph / 3.6, 2)


def normalize_owm(data: dict[str, Any], location: str) -> WeatherReading:
    """convert an openweathermap response into a WeatherReading"""
    main = data["main"]
    temp_k = main.get("temp")
    weather = data.get("weather") or []

    return WeatherReading(
        source="openweathermap",
        location=location,
        temp_c=kelvin_to_celsius(temp_k) if temp_k is not None else None,
        humidity_pct=main.get("humidity"),
        pressure_hpa=main.get("pressure"),
        wind_ms=data.get("wind", {}).get("speed"),
        description=weather[0].get("description") if weather else None,
    )


def normalize_weatherapi(data: dict[str, Any], location: str) -> WeatherReading:
    """convert a weatherapi response into a WeatherReading"""
    current = data["current"]
    wind_kph = current.get("wind_kph")

    return WeatherReading(
        source="weatherapi",
        location=location,
        temp_c=current.get("temp_c"),
        humidity_pct=current.get("humidity"),
        pressure_hpa=current.get("pressure_mb"),
        wind_ms=kph_to_ms(wind_kph) if wind_kph is not None else None,
        description=current.get("condition", {}).get("text"),
    )


def normalize_open_meteo(data: dict[str, Any], location: str) -> WeatherReading:
    """convert an open-meteo response into a WeatherReading"""
    current = data["current"]

    return WeatherReading(
        source="open-meteo",
        location=location,
        temp_c=current.get("temperature_2m"),
        humidity_pct=current.get("relative_humidity_2m"),
        pressure_hpa=current.get("pressure_msl"),
        wind_ms=current.get("wind_speed_10m"),
        description=None,
    )


NORMALIZERS = {
    "openweathermap": normalize_owm,
    "weatherapi": normalize_weatherapi,
    "open-meteo": normalize_open_meteo,
}


def normalize_all(results: list[dict[str, Any]]) -> list[WeatherReading]:
    """normalize successful fetch results, skipping failed, unknown or malformed ones"""
    readings = []
    for result in results:
        source, location = result["source"], result["location"]

        if result["error"] is not None:
            log.info("%s / %s: skipped (%s)", source, location, result["error"])
            continue

        normalizer = NORMALIZERS.get(source)
        if normalizer is None:
            log.warning(
                "%s / %s: no normalizer for source '%s'", source, location, source
            )
            continue

        try:
            reading = normalizer(result["data"], location)
            reading.elapsed_s = result.get("elapsed_s")
            readings.append(reading)
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            log.warning("%s / %s: unexpected response shape (%r)", source, location, e)

    return readings


NUMERIC_FIELDS = ("temp_c", "humidity_pct", "pressure_hpa", "wind_ms")


def aggregate(readings: list[WeatherReading]) -> dict[str, dict[str, Any]]:
    """group readings by location and compute mean, min, max, spread and n per field"""
    by_location: dict[str, list[WeatherReading]] = defaultdict(list)
    for reading in readings:
        by_location[reading.location].append(reading)

    summary: dict[str, dict[str, Any]] = {}
    for location, group in by_location.items():
        stats: dict[str, Any] = {}
        for field in NUMERIC_FIELDS:
            values = [getattr(r, field) for r in group if getattr(r, field) is not None]
            if not values:
                continue
            stats[field] = {
                "mean": round(mean(values), 2),
                "min": min(values),
                "max": max(values),
                "spread": round(max(values) - min(values), 2),
                "n": len(values),
            }
        stats["descriptions"] = {
            r.source: r.description for r in group if r.description is not None
        }
        summary[location] = stats

    return summary
