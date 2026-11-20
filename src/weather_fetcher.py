"""async fetching of raw weather data from the configured apis"""

import logging
import time

import aiohttp

log = logging.getLogger(__name__)


def build_params(source: dict, location: dict) -> dict[str, str]:
    """fill the {lat}, {lon} and {key} placeholders in a source's query params"""
    values = {
        "lat": location["lat"],
        "lon": location["lon"],
        "key": source.get("api_key", ""),
    }
    return {
        name: template.format(**values) for name, template in source["params"].items()
    }


async def fetch(session, source: dict, location: dict) -> dict:
    """fetch one source for one location as a dict with data, error and elapsed_s

    timeouts, connection and http errors are logged and stored in error, not raised
    """
    result = {
        "source": source["name"],
        "location": location["name"],
        "data": None,
        "error": None,
        "elapsed_s": None,
    }
    params = build_params(source, location)
    start = time.perf_counter()
    try:
        async with session.get(
            source["url"], params=params, headers=source.get("headers")
        ) as response:
            if response.status >= 400:
                body = await response.text()
                log.warning(
                    "%s / %s: HTTP %d: %s",
                    source["name"],
                    location["name"],
                    response.status,
                    body[:200],
                )
                result["error"] = f"HTTP {response.status}"
            else:
                result["data"] = await response.json()
    except TimeoutError:
        log.warning("%s / %s: request timed out", source["name"], location["name"])
        result["error"] = "timeout"
    except aiohttp.ClientConnectionError as e:
        log.warning(
            "%s / %s: connection error: %s", source["name"], location["name"], e
        )
        result["error"] = "connection error"

    result["elapsed_s"] = round(time.perf_counter() - start, 3)
    return result
