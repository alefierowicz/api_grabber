# api_grabber

## config

```sh
cp config.example.json config.json
```

Then fill in your `api_key` for `openweathermap` and `weatherapi`. Open-Meteo doesn't need one.

- `locations`: the places to check, each with a `name`, `lat` and `lon`
- `sources`: the APIs to call. `{lat}`, `{lon}` and `{key}` in `params` are filled in for each location
- `settings.timeout_s`: the request timeout in seconds (optional, default 10)

## run

```sh
uv run src/main.py
```
