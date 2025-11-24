"""Admin panel handlers - main sections"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.admin.keyboards import admin_panel_kb
from config import ADMIN_TG_ID


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass

router = Router()


@router.callback_query(F.data == 'admin_panel')
async def show_admin_panel(callback: CallbackQuery, t):
    """Show admin panel - only accessible to admin"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    # Security check: only admin can access
    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await callback.message.edit_text(
        t('admin_panel_welcome'),
        reply_markup=admin_panel_kb(t)
    )


@router.callback_query(F.data == 'admin_stats')
async def admin_stats(callback: CallbackQuery, t):
    """Show bot statistics"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    from datetime import datetime, timedelta
    from decimal import Decimal
    from sqlalchemy import select, func
    from app.repo.db import get_session
    from app.repo.models import User, Payment, Config

    async with get_session() as session:
        now = datetime.utcnow()

        # User statistics
        result = await session.execute(select(func.count(User.tg_id)))
        total_users = result.scalar() or 0

        # New users by time periods
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        result = await session.execute(
            select(func.count(User.tg_id)).where(User.created_at >= day_ago)
        )
        new_users_24h = result.scalar() or 0

        result = await session.execute(
            select(func.count(User.tg_id)).where(User.created_at >= week_ago)
        )
        new_users_7d = result.scalar() or 0

        result = await session.execute(
            select(func.count(User.tg_id)).where(User.created_at >= month_ago)
        )
        new_users_30d = result.scalar() or 0

        # Subscription statistics
        result = await session.execute(
            select(func.count(User.tg_id)).where(User.subscription_end > now)
        )
        active_subs = result.scalar() or 0

        result = await session.execute(
            select(func.count(User.tg_id)).where(
                User.subscription_end.isnot(None),
                User.subscription_end <= now
            )
        )
        expired_subs = result.scalar() or 0

        result = await session.execute(
            select(func.count(User.tg_id)).where(User.subscription_end.is_(None))
        )
        no_subs = result.scalar() or 0

        # Revenue statistics
        result = await session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == 'confirmed')
        )
        total_revenue = result.scalar() or Decimal(0)
        if isinstance(total_revenue, Decimal):
            total_revenue = float(total_revenue)

        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= day_ago
            )
        )
        today_revenue = result.scalar() or Decimal(0)
        if isinstance(today_revenue, Decimal):
            today_revenue = float(today_revenue)

        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= week_ago
            )
        )
        week_revenue = result.scalar() or Decimal(0)
        if isinstance(week_revenue, Decimal):
            week_revenue = float(week_revenue)

        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= month_ago
            )
        )
        month_revenue = result.scalar() or Decimal(0)
        if isinstance(month_revenue, Decimal):
            month_revenue = float(month_revenue)

        # Config statistics
        result = await session.execute(select(func.count(Config.id)))
        total_configs = result.scalar() or 0

        result = await session.execute(
            select(func.count(Config.id)).where(Config.deleted == False)
        )
        active_configs = result.scalar() or 0

        deleted_configs = total_configs - active_configs

    stats_text = t('admin_bot_stats',
                   total_users=total_users,
                   new_users_24h=new_users_24h,
                   new_users_7d=new_users_7d,
                   new_users_30d=new_users_30d,
                   active_subs=active_subs,
                   expired_subs=expired_subs,
                   no_subs=no_subs,
                   total_revenue=total_revenue,
                   today_revenue=today_revenue,
                   week_revenue=week_revenue,
                   month_revenue=month_revenue,
                   total_configs=total_configs,
                   active_configs=active_configs,
                   deleted_configs=deleted_configs)

    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_panel_kb(t)
    )


