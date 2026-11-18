def build_params(source: dict, location: dict) -> dict[str, str]:
    values = {
        "lat": location["lat"],
        "lon": location["lon"],
        "key": source.get("api_key", ""),
    }
    return {name: template.format(**values) for name, template in source["params"].items()}


async def fetch(session, source: dict, location: dict) -> dict:
    params = build_params(source, location)
    async with session.get(source["url"], params=params, headers=source.get("headers")) as response:
        data = await response.json()
        print(f"[{source['name']} / {location['name']}] got back: {data}\n")
        return {"source": source["name"], "location": location["name"], "data": data}
