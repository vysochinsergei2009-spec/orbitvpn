"""Admin handlers router aggregation"""

from aiogram import Router

from . import panel, servers, broadcast


def get_router() -> Router:
    """Get admin handlers router with all sub-routers included"""
    admin_router = Router()

    admin_router.include_router(panel.router)
    admin_router.include_router(servers.router)
    admin_router.include_router(broadcast.router)

    return admin_router


router = get_router()
