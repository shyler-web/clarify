import os
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "signals.yaml"


class ConfigError(Exception):
    pass


def _load() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_signal_weights() -> dict[str, float]:
    return _load()["weights"]


def load_thresholds() -> dict[str, dict]:
    return _load()["thresholds"]


def get_env(key: str) -> str:
    try:
        return os.environ[key]
    except KeyError:
        raise ConfigError(f"Environment variable '{key}' is not set.") from None