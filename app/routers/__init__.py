"""Unified router - combines all bot handlers"""

from aiogram import Router
from app.middleware.admin import AdminMiddleware

from .admin import router as admin_router
from .user import setup_handlers as setup_user_handlers

__all__ = ['router']


def get_router() -> Router:
    """Get unified router with all handlers"""
    main_router = Router()
    
    # Add admin middleware to admin router
    admin_router.message.middleware(AdminMiddleware())
    admin_router.callback_query.middleware(AdminMiddleware())
    
    # Include all routers
    main_router.include_router(admin_router)
    main_router.include_router(setup_user_handlers())
    
    return main_router


# Export unified router
router = get_router()
