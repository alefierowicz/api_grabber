"""Tests for config loading."""
import json

from main import load_config

SAMPLE_CONFIG = {
    "locations": [{"name": "Białystok", "lat": 53.1333, "lon": 23.1643}],
    "sources": [
        {
            "name": "open-meteo",
            "url": "https://api.open-meteo.com/v1/forecast",
            "params": {"latitude": "{lat}", "longitude": "{lon}"},
        }
    ],
}


def test_load_config_reads_locations_and_sources(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(SAMPLE_CONFIG, ensure_ascii=False), encoding="utf-8")

    config = load_config(path)

    assert config == SAMPLE_CONFIG
    assert config["locations"][0]["name"] == "Białystok"
