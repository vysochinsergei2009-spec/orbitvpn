import json
from pathlib import Path
from functools import cached_property
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvSettingsFile(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True, 
        extra="ignore"
    )
    
    BOT_TOKEN: str
    ADMIN_TG_IDS: list[int]
    SUPPORT_USER: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    REDIS_URL: str = "redis://localhost"
    PANEL_HOST: str
    PANEL_USERNAME: str
    PANEL_PASSWORD: str
    MAX_IPS_PER_CONFIG: int = 2
    TON_ADDRESS: str
    TONAPI_URL: str = "https://tonapi.io"
    TONAPI_KEY: str
    CRYPTOBOT_TOKEN: str
    CRYPTOBOT_TESTNET: bool = False
    YOOKASSA_ID: str
    YOOKASSA_KEY: str
    YOOKASSA_ID_T: str
    YOOKASSA_KEY_T: str
    YOOKASSA_T: bool = False
    MIN_PAYMENT_AMOUNT: int = 200
    MAX_PAYMENT_AMOUNT: int = 100000
    TELEGRAM_STARS_RATE: float = 1.5
    FREE_TRIAL_DAYS: int = 3
    PAYMENT_TIMEOUT_MINUTES: int = 15
    REFERRAL_BONUS: int
    IS_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_AIOGRAM: bool = False
    
    @field_validator("ADMIN_TG_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return json.loads(v.replace(" ", ""))
        return v

    @cached_property
    def plans(self) -> dict:
        plans_path = Path(__file__).parent / "plans.json"
        return json.loads(plans_path.read_text(encoding="utf-8"))
    
    @cached_property
    def links(self) -> dict:
        links_path = Path(__file__).parent / "links.json"
        return json.loads(links_path.read_text(encoding="utf-8"))
    
    def is_admin(self, chat_id: int) -> bool:
        return chat_id in self.ADMIN_TG_IDS