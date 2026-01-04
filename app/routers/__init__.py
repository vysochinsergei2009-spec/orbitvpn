from aiogram import Router
from app.settings.middlewares import AdminMiddleware

from .user import setup_handlers as setup_user_handlers

__all__ = ['router']


def get_router() -> Router:
    main_router = Router()
    
    main_router.include_router(setup_user_handlers())
    
    return main_router

router = get_router()
