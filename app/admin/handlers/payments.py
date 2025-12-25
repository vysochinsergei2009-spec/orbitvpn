"""Admin handlers for payment statistics"""

from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from app.admin.keyboards import admin_payments_kb
from app.repo.db import get_session
from app.repo.models import Payment
from config import ADMIN_TG_IDS


router = Router()


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == 'admin_payments')
async def show_admin_payments(callback: CallbackQuery, t):
    """Show payment statistics"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    async with get_session() as session:
        # Total payments count by status
        result = await session.execute(
            select(
                func.count(Payment.id).label('total'),
                func.sum(func.cast(Payment.status == 'confirmed', func.Integer)).label('confirmed'),
                func.sum(func.cast(Payment.status == 'pending', func.Integer)).label('pending')
            )
        )
        row = result.one()
        total_payments = row.total or 0
        confirmed_payments = row.confirmed or 0
        pending_payments = row.pending or 0
        failed_payments = total_payments - confirmed_payments - pending_payments

        # Total revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == 'confirmed')
        )
        total_revenue = result.scalar() or Decimal(0)
        if isinstance(total_revenue, Decimal):
            total_revenue = float(total_revenue)

        # Revenue by time periods
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Today's revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= day_ago
            )
        )
        today_revenue = result.scalar() or Decimal(0)
        if isinstance(today_revenue, Decimal):
            today_revenue = float(today_revenue)

        # Week revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= week_ago
            )
        )
        week_revenue = result.scalar() or Decimal(0)
        if isinstance(week_revenue, Decimal):
            week_revenue = float(week_revenue)

        # Month revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= month_ago
            )
        )
        month_revenue = result.scalar() or Decimal(0)
        if isinstance(month_revenue, Decimal):
            month_revenue = float(month_revenue)

        # Payment methods breakdown
        result = await session.execute(
            select(Payment.method, func.count(Payment.id), func.sum(Payment.amount))
            .where(Payment.status == 'confirmed')
            .group_by(Payment.method)
        )
        methods_data = result.all()

    stats_text = t('admin_payments_stats',
                   total=total_payments,
                   confirmed=confirmed_payments,
                   pending=pending_payments,
                   failed=failed_payments,
                   total_revenue=total_revenue,
                   today_revenue=today_revenue,
                   week_revenue=week_revenue,
                   month_revenue=month_revenue)

    # Add methods breakdown if available
    if methods_data:
        methods_lines = []
        for method, count, amount in methods_data:
            if amount:
                amount_val = float(amount) if isinstance(amount, Decimal) else amount
                methods_lines.append(f"• {method}: {count} платежей ({amount_val:.2f} RUB)")
            else:
                methods_lines.append(f"• {method}: {count} платежей")

        methods_stats = '\n'.join(methods_lines)
        stats_text += t('admin_payment_methods', methods_stats=methods_stats)

    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_payments_kb(t)
    )


@router.callback_query(F.data == 'admin_recent_payments')
async def show_recent_payments(callback: CallbackQuery, t):
    """Show recent payments list"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    async with get_session() as session:
        # Get last 15 payments
        result = await session.execute(
            select(Payment)
            .order_by(Payment.created_at.desc())
            .limit(15)
        )
        payments = result.scalars().all()

    if not payments:
        await callback.message.edit_text(
            t('admin_no_recent_payments'),
            reply_markup=admin_payments_kb(t)
        )
        return

    payment_lines = []
    for payment in payments:
        date_str = payment.created_at.strftime("%Y-%m-%d %H:%M") if payment.created_at else "N/A"
        amount_val = float(payment.amount) if isinstance(payment.amount, Decimal) else payment.amount

        payment_lines.append(
            t('admin_payment_item',
              amount=amount_val,
              method=payment.method,
              tg_id=payment.tg_id,
              status=payment.status,
              date=date_str)
        )

    payments_text = t('admin_recent_payments') + '\n\n' + '\n\n'.join(payment_lines)

    await callback.message.edit_text(
        payments_text,
        reply_markup=admin_payments_kb(t)
    )
