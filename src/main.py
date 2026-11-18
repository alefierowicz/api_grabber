import aiohttp
import asyncio
import json
import logging
from pathlib import Path
from weather_fetcher import fetch

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
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
    asyncio.run(main())

if __name__ == '__main__':
    run()
