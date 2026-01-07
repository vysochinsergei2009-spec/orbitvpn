from aiogram import Bot
#from ..config import env
from config import BOT_TOKEN

def create_bot() -> Bot:
    return Bot(token=BOT_TOKEN)