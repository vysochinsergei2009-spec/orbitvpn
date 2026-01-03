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
    REDIS_URL: str = "redis://localhost"
    PORT: int = 5000
    VPN_PANEL_TYPE: str = "marzban"
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
    
    def is_admin(self, chat_id: int) -> bool:
        return chat_id in self.ADMIN_TG_IDS