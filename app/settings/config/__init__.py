import json
from pathlib import Path
from typing import Final

from ._env import EnvSettingsFile

env = EnvSettingsFile()

BASE_PATH = Path(__file__).parent

PLANS: Final = json.loads(
    (BASE_PATH / "plans.json").read_text(encoding="utf-8")
)

LINKS: Final = json.loads(
    (BASE_PATH / "links.json").read_text(encoding="utf-8")
)

__all__ = ["env", "PLANS", "LINKS"]