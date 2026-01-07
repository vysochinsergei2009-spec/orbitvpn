from aiogram import Bot
from app.settings.config import env

def create_bot() -> Bot:
    return Bot(token=env.BOT_TOKEN)