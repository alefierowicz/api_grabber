import logging

import aiohttp

log = logging.getLogger(__name__)


def build_params(source: dict, location: dict) -> dict[str, str]:
    values = {
        "lat": location["lat"],
        "lon": location["lon"],
        "key": source.get("api_key", ""),
    }
    return {name: template.format(**values) for name, template in source["params"].items()}


async def fetch(session, source: dict, location: dict) -> dict:
    result = {"source": source["name"], "location": location["name"], "data": None, "error": None}
    params = build_params(source, location)
    try:
        async with session.get(source["url"], params=params, headers=source.get("headers")) as response:
            if response.status >= 400:
                body = await response.text()
                log.warning(
                    "%s / %s: HTTP %d: %s",
                    source["name"], location["name"], response.status, body[:200],
                )
                result["error"] = f"HTTP {response.status}"
                return result
            result["data"] = await response.json()
    except TimeoutError:
        log.warning("%s / %s: request timed out", source["name"], location["name"])
        result["error"] = "timeout"
        return result
    except aiohttp.ClientConnectionError as e:
        log.warning("%s / %s: connection error: %s", source["name"], location["name"], e)
        result["error"] = "connection error"
        return result

    return result
