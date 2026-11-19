import aiohttp
import asyncio
import json
import logging
import sys
from pathlib import Path
from weather_fetcher import fetch

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class ConfigError(Exception):
    pass


def _require_list(config: dict, key: str) -> list:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ConfigError(f"'{key}' must be a non-empty list")
    return value


def validate_config(config: dict) -> None:
    if not isinstance(config, dict):
        raise ConfigError("top level must be a JSON object")

    for i, loc in enumerate(_require_list(config, "locations")):
        for key in ("name", "lat", "lon"):
            if key not in loc:
                raise ConfigError(f"locations[{i}]: missing '{key}'")
        for key in ("lat", "lon"):
            if isinstance(loc[key], bool) or not isinstance(loc[key], (int, float)):
                raise ConfigError(f"locations[{i}] ({loc['name']}): '{key}' must be a number")

    for i, src in enumerate(_require_list(config, "sources")):
        for key in ("name", "url", "params"):
            if key not in src:
                raise ConfigError(f"sources[{i}]: missing '{key}'")
        if not isinstance(src["params"], dict):
            raise ConfigError(f"sources[{i}] ({src['name']}): 'params' must be an object")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise ConfigError(
            f"config file not found: {path} (copy config.example.json to config.json)"
        ) from None
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"invalid JSON in {path}, line {e.lineno} column {e.colno}: {e.msg}"
        ) from None

    validate_config(config)
    log.info(
        "Loaded config from %s: %d locations, %d sources",
        path, len(config["locations"]), len(config["sources"]),
    )
    return config

async def main() -> None:
    config = load_config()

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch(session, source, location)
            for location in config["locations"]
            for source in config["sources"]
        ]
        results = await asyncio.gather(*tasks)

def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        asyncio.run(main())
    except ConfigError as e:
        log.error("Config error: %s", e)
        sys.exit(1)

if __name__ == '__main__':
    run()
