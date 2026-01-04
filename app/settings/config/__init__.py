import json
from typing import Final
from pathlib import Path

from ._env import EnvSettingsFile

env = EnvSettingsFile()

PLANS = json.loads(
    Path(__file__).with_name("plans.json").read_text(encoding="utf-8")
)

INSTALL_GUIDE_BASE_URL: Final[str] = "https://orbitcorp.space:2053"
INSTALL_GUIDE_URLS: Final[dict[str, str]] = {
    "ru": f"{INSTALL_GUIDE_BASE_URL}/install/ru",
    "en": f"{INSTALL_GUIDE_BASE_URL}/install/en",
}
PRIVACY_POLICY_URLS: Final[dict[str, str]] = {
    "ru": f"{INSTALL_GUIDE_BASE_URL}/policy/ru",
    "en": f"{INSTALL_GUIDE_BASE_URL}/policy/en",
}

IS_LOGGING: Final[bool] = True
LOG_LEVEL: Final[str] = "INFO"  # Options: "INFO", "DEBUG", "ERROR"
LOG_AIOGRAM: Final[bool] = False

__all__ = ["env", "PLANS"]
