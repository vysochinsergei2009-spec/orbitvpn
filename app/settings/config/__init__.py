import json
from typing import Final
from pathlib import Path

from ._env import EnvSettingsFile

env = EnvSettingsFile()

__all__ = ["env"]
