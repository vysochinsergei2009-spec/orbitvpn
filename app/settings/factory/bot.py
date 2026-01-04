from aiogram import Bot
from ..config import env

def create_bot() -> Bot:
    return Bot(token=env.BOT_TOKEN)