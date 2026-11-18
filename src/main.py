import aiohttp
import asyncio
from weather_fetcher import get_OpenWeatherMap_url, get_WeatherAPI_url, fetch


async def main() -> None:
    weatherAPI_tgt: str = get_WeatherAPI_url()
    openWeatherMap_tgt: str = get_OpenWeatherMap_url()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, openWeatherMap_tgt), fetch(session, weatherAPI_tgt)]
        result = await asyncio.gather(*tasks)

def run() -> None:
    asyncio.run(main())

if __name__ == '__main__':
    run()
