#!/usr/bin/env python3
"""
Test script to manually check notification system.
Usage: python3 test_notifications.py
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from app.repo.db import get_session
from app.repo.models import User
from config import bot


async def check_notifications():
    """Check how many users would receive notifications"""

    print("\n" + "="*60)
    print("🔔 ПРОВЕРКА СИСТЕМЫ УВЕДОМЛЕНИЙ")
    print("="*60 + "\n")

    async with get_session() as session:
        now = datetime.utcnow()

        # Users with subscriptions expiring in 3 days
        threshold_3d = now + timedelta(days=3)
        threshold_3d_lower = now + timedelta(days=1, hours=1)

        result_3d = await session.execute(
            select(User).where(
                User.subscription_end.isnot(None),
                User.subscription_end > threshold_3d_lower,
                User.subscription_end <= threshold_3d,
                User.notifications == True
            )
        )
        users_3d = result_3d.scalars().all()

        # Users with subscriptions expiring in 1 day
        threshold_1d = now + timedelta(days=1, hours=1)
        threshold_1d_lower = now + timedelta(hours=1)

        result_1d = await session.execute(
            select(User).where(
                User.subscription_end.isnot(None),
                User.subscription_end > threshold_1d_lower,
                User.subscription_end <= threshold_1d,
                User.notifications == True
            )
        )
        users_1d = result_1d.scalars().all()

        # Users with expired subscriptions (within last 24 hours)
        threshold_expired = now - timedelta(days=1)

        result_expired = await session.execute(
            select(User).where(
                User.subscription_end.isnot(None),
                User.subscription_end <= now,
                User.subscription_end >= threshold_expired,
                User.notifications == True
            )
        )
        users_expired = result_expired.scalars().all()

        # All users with notifications disabled
        result_disabled = await session.execute(
            select(User).where(User.notifications == False)
        )
        users_disabled = result_disabled.scalars().all()

        # Print results
        print(f"📅 За 3 дня до истечения:     {len(users_3d)} пользователей")
        print(f"⏰ За 1 день до истечения:     {len(users_1d)} пользователей")
        print(f"✅ Подписка истекла (24ч):     {len(users_expired)} пользователей")
        print(f"🔕 Уведомления отключены:      {len(users_disabled)} пользователей")

        print("\n" + "-"*60)
        print("ДЕТАЛИ ИСТЕКШИХ ПОДПИСОК:")
        print("-"*60 + "\n")

        if users_expired:
            for user in users_expired[:5]:  # Show first 5
                time_ago = now - user.subscription_end
                hours_ago = time_ago.total_seconds() / 3600
                print(f"  User {user.tg_id}: истекла {hours_ago:.1f}ч назад (язык: {user.lang})")

            if len(users_expired) > 5:
                print(f"  ... и ещё {len(users_expired) - 5} пользователей")
        else:
            print("  Нет пользователей с недавно истекшими подписками")

        print("\n" + "="*60)
        print("✓ Проверка завершена")
        print("="*60 + "\n")

        # Show sample messages
        print("📝 ПРИМЕРЫ УВЕДОМЛЕНИЙ:\n")

        from app.locales.locales import get_translator
        t_ru = get_translator('ru')
        t_en = get_translator('en')

        print("🇷🇺 Русский (истекшая подписка):")
        print(f"   {t_ru('sub_expired_1')}\n")

        print("🇬🇧 English (expired subscription):")
        print(f"   {t_en('sub_expired_1')}\n")

        print("💡 Все уведомления содержат кнопку [Баланс] для пополнения\n")


if __name__ == "__main__":
    asyncio.run(check_notifications())
