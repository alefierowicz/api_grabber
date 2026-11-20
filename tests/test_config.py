"""tests for config loading"""

import json

import pytest

from main import ConfigError, load_config

pytestmark = pytest.mark.config


def without_lon(config):
    del config["locations"][0]["lon"]
    return json.dumps(config)


def with_zero_timeout(config):
    config["settings"] = {"timeout_s": 0}
    return json.dumps(config)


def broken_json(config):
    return '{\n  "locations": [,]\n}'


def test_load_config(config_file, sample_config):
    assert load_config(config_file) == sample_config


@pytest.mark.parametrize(
    ("make_content", "message"),
    [
        pytest.param(broken_json, "line 2", id="broken-json"),
        pytest.param(without_lon, r"locations\[0\]: missing 'lon'", id="missing-lon"),
        pytest.param(
            with_zero_timeout, "timeout_s must be a positive number", id="zero-timeout"
        ),
    ],
)
def test_invalid_config_rejected(tmp_path, sample_config, make_content, message):
    path = tmp_path / "config.json"
    path.write_text(make_content(sample_config), encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_config(path)
