from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvSettingsFile(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )
    
    BOT_TOKEN: str
    ADMIN_TG_IDS: list[int]
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = 5432
    REDIS_URL: str = "redis://localhost"
    PORT: int = 5000
    VPN_PANEL_TYPE: str = "marzneshin"
    PANEL_HOST: str
    PANEL_USERNAME: str
    PANEL_PASSWORD: str
    MAX_IPS_PER_CONFIG: int = 2
    TON_ADDRESS: str
    TONAPI_URL: str = "https://tonapi.io"
    TONAPI_KEY: str
    CRYPTOBOT_TOKEN: str
    CRYPTOBOT_TESTNET: bool = False
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_TEST_SHOP_ID: str
    YOOKASSA_TEST_SECRET_KEY: str
    YOOKASSA_TESTNET: bool = False
    MIN_PAYMENT_AMOUNT: int = 200
    MAX_PAYMENT_AMOUNT: int = 100000
    TELEGRAM_STARS_RATE: float = 1.5
    FREE_TRIAL_DAYS: int = 3
    PAYMENT_TIMEOUT_MINUTES: int = 15
    REFERRAL_BONUS: int
    IS_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_AIOGRAM: bool = False
    PUBLIC_SUB_URL: str = "https://cdn.orbitcorp.space"
    
    def is_admin(self, chat_id: int) -> bool:
        return chat_id in self.ADMIN_TG_IDS