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
