import logging
import uuid
import asyncio
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from gateway import *
from app.payments.models import PaymentResult, PaymentMethod
from app.db.payments import PaymentRepository
from app.db.user import UserRepository
from app.db.db import get_session
from app.db.cache import get_redis
from app.settings.factory import create_bot

LOG = logging.getLogger(__name__)
bot = create_bot()
class PaymentManager:
    def __init__(self, session, redis_client=None):
        self.session = session
        self.redis_client = redis_client
        self.payment_repo = PaymentRepository(session, redis_client)
        self.gateways: dict[PaymentMethod, BasePaymentGateway] = {
            PaymentMethod.TON: TonGateway(session, redis_client, bot=bot),
            PaymentMethod.STARS: TelegramStarsGateway(bot, session, redis_client),
            PaymentMethod.CRYPTOBOT: CryptoBotGateway(session, redis_client, bot=bot),
            PaymentMethod.YOOKASSA: YooKassaGateway(session, redis_client, bot=bot),
        }
        self.user_repo = UserRepository(session, redis_client)
        self.polling_task: Optional[asyncio.Task] = None

    async def create_payment(
        self,
        t,
        tg_id: int,
        method: PaymentMethod,
        amount: Decimal,
        chat_id: Optional[int] = None,
    ) -> PaymentResult:
        try:
            from app.db.models import User
            from sqlalchemy import select

            result = await self.session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {tg_id} not found")

            active_payments = await self.payment_repo.get_active_pending_payments(tg_id)
            if active_payments:
                LOG.info(f"User {tg_id} has {len(active_payments)} active payment(s). Auto-canceling...")
                for payment in active_payments:
                    try:
                        await self.cancel_payment(payment['id'])
                    except Exception as e:
                        LOG.error(f"Failed to cancel payment {payment['id']}: {e}")

            currency = "RUB"
            comment = None
            expected_crypto_amount = None

            if method == PaymentMethod.TON:
                comment = uuid.uuid4().hex[:10]
                from app.settings.utils.rates import get_ton_price
                ton_price = await get_ton_price()
                expected_crypto_amount = (Decimal(amount) / ton_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            payment_id = await self.payment_repo.create_payment(
                tg_id=tg_id,
                method=method.value,
                amount=amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                currency=currency,
                comment=comment,
                expected_crypto_amount=expected_crypto_amount
            )

            try:
                gateway = self.gateways[method]
                result = await gateway.create_payment(
                    t,
                    tg_id=tg_id,
                    amount=amount,
                    chat_id=chat_id,
                    payment_id=payment_id,
                    comment=comment
                )

                LOG.info(f"Payment created: {method} for user {tg_id}, amount {amount}, id={payment_id}")
                if method in [PaymentMethod.TON, PaymentMethod.CRYPTOBOT, PaymentMethod.YOOKASSA]:
                    await self.start_polling_if_needed()
                return result
            except Exception as gateway_error:
                LOG.error(f"Gateway error for payment {payment_id}: {type(gateway_error).__name__}: {gateway_error}")
                try:
                    await self.cancel_payment(payment_id)
                    LOG.info(f"Cancelled payment {payment_id} due to gateway error")
                except Exception as cancel_err:
                    LOG.error(f"Failed to cancel payment {payment_id}: {cancel_err}", exc_info=True)
                raise
        except Exception as e:
            LOG.error(f"Create payment error for user {tg_id}: {type(e).__name__}: {e}")
            raise

    async def cancel_payment(self, payment_id: int):
        payment = await self.payment_repo.get_payment(payment_id)
        if not payment or payment['status'] != 'pending':
            LOG.warning(f"Attempted to cancel payment {payment_id} which is not pending.")
            return

        LOG.info(f"Cancelling payment {payment_id} for user {payment['tg_id']}.")
        
        try:
            method = PaymentMethod(payment['method'])
            gateway = self.gateways.get(method)
            
            if gateway and hasattr(gateway, 'cancel_payment'):
                await gateway.cancel_payment(payment_id)
            
        except Exception as e:
            LOG.error(f"Remote cancellation for payment {payment_id} failed: {e}", exc_info=True)

        await self.payment_repo.update_payment_status(payment_id, 'cancelled')
        LOG.info(f"Locally cancelled payment {payment_id}.")

    async def confirm_payment(self, payment_id: int, tg_id: int, amount: Decimal, tx_hash: Optional[str] = None):
        try:
            await self.user_repo.change_balance(tg_id, amount)

            if tx_hash:
                await self.payment_repo.update_payment_status(payment_id, "confirmed", tx_hash)

            LOG.info(f"Payment {payment_id} confirmed: +{amount} for user {tg_id}, tx={tx_hash}")

            return None
        except Exception as e:
            LOG.error(f"Confirm payment error for user {tg_id}: {type(e).__name__}: {e}")
            raise

    async def start_polling_if_needed(self):
        if self.polling_task is None or self.polling_task.done():
            self.polling_task = asyncio.create_task(self.run_polling_loop())

    async def run_polling_loop(self):
        while True:
            try:
                async with get_session() as session:
                    redis_client = await get_redis()
                    temp_payment_repo = PaymentRepository(session, redis_client)

                    ton_pendings = await temp_payment_repo.get_pending_payments(PaymentMethod.TON.value)
                    if ton_pendings:
                        from app.settings.utils.updater import TonTransactionsUpdater
                        updater = TonTransactionsUpdater()
                        await updater.run_once()

                    cryptobot_pendings = await temp_payment_repo.get_pending_payments(PaymentMethod.CRYPTOBOT.value)
                    if cryptobot_pendings:
                        for payment in cryptobot_pendings:
                            async with get_session() as check_session:
                                check_redis = await get_redis()
                                check_gateway = self.gateways[PaymentMethod.CRYPTOBOT].__class__(check_session, check_redis, bot=bot)
                                await check_gateway.check_payment(payment['id'])

                    yookassa_pendings = await temp_payment_repo.get_pending_or_recent_expired_payments(
                        PaymentMethod.YOOKASSA.value,
                        expired_hours=1
                    )
                    if yookassa_pendings:
                        for payment in yookassa_pendings:
                            async with get_session() as check_session:
                                check_redis = await get_redis()
                                check_gateway = self.gateways[PaymentMethod.YOOKASSA].__class__(check_session, check_redis, bot=bot)
                                await check_gateway.check_payment(payment['id'])

                    if not ton_pendings and not cryptobot_pendings and not yookassa_pendings:
                        break
            except Exception as e:
                LOG.error(f"Polling loop error: {type(e).__name__}: {e}")
            await asyncio.sleep(60)

    async def check_payment(self, payment_id: int) -> bool:
        try:
            payment = await self.payment_repo.get_payment(payment_id)
            if not payment or payment['status'] != 'pending':
                return False

            gateway = self.gateways[PaymentMethod(payment['method'])]
            confirmed = await gateway.check_payment(payment_id)



            return confirmed
        except Exception as e:
            LOG.error(f"Check payment error for payment {payment_id}: {type(e).__name__}: {e}")
            return False

    async def get_pending_payments(self, method: Optional[PaymentMethod | str] = None):
        return await self.payment_repo.get_pending_payments(method if method else None)

    async def close(self):
        for gateway in self.gateways.values():
            if hasattr(gateway, 'close'):
                await gateway.close()
        if self.polling_task:
            self.polling_task.cancel()