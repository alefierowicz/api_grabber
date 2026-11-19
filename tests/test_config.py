"""tests for config loading."""
import copy
import json
from pathlib import Path

import pytest

from main import ConfigError, load_config

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


def write_config(tmp_path, data) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_config_reads_locations_and_sources(tmp_path):
    config = load_config(write_config(tmp_path, SAMPLE_CONFIG))

    assert config == SAMPLE_CONFIG
    assert config["locations"][0]["name"] == "Białystok"


def test_missing_file_raises_config_error(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.json")


def test_invalid_json_reports_line(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{\n  "locations": [,]\n}', encoding="utf-8")

    with pytest.raises(ConfigError, match="line 2"):
        load_config(path)


def test_location_missing_key_rejected(tmp_path):
    data = copy.deepcopy(SAMPLE_CONFIG)
    del data["locations"][0]["lon"]

    with pytest.raises(ConfigError, match=r"locations\[0\]: missing 'lon'"):
        load_config(write_config(tmp_path, data))


def test_invalid_timeout_rejected(tmp_path):
    data = copy.deepcopy(SAMPLE_CONFIG)
    data["settings"] = {"timeout_s": 0}

    with pytest.raises(ConfigError, match="timeout_s must be a positive number"):
        load_config(write_config(tmp_path, data))
