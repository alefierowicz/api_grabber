"""Normalization & aggregation of weather data from multiple sources"""
from dataclasses import dataclass
from typing import Any


@dataclass
class WeatherReading:
    source: str
    location: str
    temp_c: float | None
    humidity_pct: float | None
    pressure_hpa: float | None
    wind_ms: float | None
    description: str | None


def kelvin_to_celsius(k: float) -> float:
    return round(k - 273.15, 2)


def kph_to_ms(kph: float) -> float:
    return round(kph / 3.6, 2)


def normalize_owm(data: dict[str, Any], location: str) -> WeatherReading:
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
