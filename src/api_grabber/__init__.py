import aiohttp
import asyncio
import json

LAT, LON = 53.13333, 23.16433

async def fetch(session, url) -> None:
    async with session.get(url) as response:
        data = await response.json()
        print(f"got back: {data}\n\n\n")
        return data

def get_API_key(config: str) -> str:
    with open('config.json') as f:
        match config:
            case "wAPI_config":
                api_key = json.load(f)[config]['API_KEY']
            case "owm_config":
                api_key = json.load(f)[config]['API_KEY']
            case _:
                api_key = None
        return api_key

def get_WeatherAPI_url() -> str: 
    key = get_API_key("wAPI_config")
    tgt_url = f"https://api.weatherapi.com/v1/current.json?key={key}&q={LAT},{LON}&aqi=no"
    
    return tgt_url

def get_OpenWeatherMap_url() -> str:
    key = get_API_key("owm_config")
    tgt_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={key}"

    return tgt_url


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
