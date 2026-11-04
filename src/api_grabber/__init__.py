import aiohttp
import asyncio
import json

LAT, LON = 53.13333, 23.16433

async def fetch(session, url) -> None:
    async with session.get(url) as response:
        data = await response.json()
        print(f"got back: {data}")
        return data

async def main() -> None:
    # https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
    with open('config.json') as f:
        api_key = json.load(f)['config']['API_KEY']
    tgt_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={api_key}"

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, tgt_url)]
        result = await asyncio.gather(*tasks)
        print(result)

def run() -> None:
    asyncio.run(main())

if __name__ == '__main__':
    run()