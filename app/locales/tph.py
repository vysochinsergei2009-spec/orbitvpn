from typing import Optional


class TelegraphManager:
    CACHE_TTL = 86400 * 30
    CACHE_KEY_PREFIX = "telegraph:install:"
    STATIC_BASE_URL = "https://install.orbitcorp.space:8443"

    def __init__(self):
        pass

    async def get_install_guide_url(self, locale: str = "ru") -> str:
        if locale not in ("ru", "en"):
            locale = "ru"

        return f"{self.STATIC_BASE_URL}/{locale}.html"


_manager: Optional[TelegraphManager] = None


def get_telegraph_manager() -> TelegraphManager:
    global _manager
    if _manager is None:
        _manager = TelegraphManager()
    return _manager


async def get_install_guide_url(locale: str = "ru") -> str:
    manager = get_telegraph_manager()
    return await manager.get_install_guide_url(locale)
