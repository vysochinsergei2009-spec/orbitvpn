import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from pytonapi import AsyncTonapi
from pytonapi.utils import to_amount, raw_to_userfriendly
from sqlalchemy.exc import IntegrityError

from app.db.db import get_session
from app.payments import PaymentManager
from app.models.payments import PaymentMethod
from app.db.models import TonTransaction
from app.db.cache import get_redis
from app.settings.config import env

LOG = logging.getLogger(__name__)

_last_lt = 0


async def fetch_new_transactions(tonapi: AsyncTonapi, limit: int = 50) -> list:
    global _last_lt
    
    try:
        result = await tonapi.blockchain.get_account_transactions(
            account_id=env.TON_ADDRESS,
            limit=limit
        )
        txs = []
        now = datetime.utcnow()
        min_time = now - timedelta(minutes=env.PAYMENT_TIMEOUT_MINUTES * 2)

        for tx in result.transactions:
            lt = int(tx.lt)
            try:
                created_at = datetime.utcfromtimestamp(int(tx.utime))
            except Exception:
                LOG.debug("Skipping tx with invalid utime: %s", getattr(tx, "hash", "<no-hash>"))
                continue

            if lt <= _last_lt or created_at < min_time:
                continue
            _last_lt = max(_last_lt, lt)
            txs.append(tx)
        
        return txs
        
    except Exception as e:
        LOG.error(f"Fetch TON transactions error: {e}")
        return []


async def insert_transactions(txs: list) -> None:
    if not txs:
        return

    async with get_session() as session:
        for tx in txs:
            try:
                tx_hash = tx.hash
                amount = Decimal(to_amount(getattr(tx.in_msg, "value", 0))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                comment = (
                    tx.in_msg.decoded_body.get("text", "")
                    if getattr(tx.in_msg, "decoded_op_name", "") == "text_comment"
                    else ""
                )
                source = getattr(tx.in_msg, "source", None)
                sender = (
                    raw_to_userfriendly(source.address.root)
                    if source and hasattr(source, "address") and hasattr(source.address, "root")
                    else None
                )
                created_at = datetime.utcfromtimestamp(int(tx.utime))

                txn = TonTransaction(
                    tx_hash=tx_hash,
                    amount=amount,
                    comment=comment,
                    sender=sender,
                    created_at=created_at,
                    processed_at=None
                )
                session.add(txn)
            except Exception as e:
                LOG.error(f"Insert transaction error: {e}")
        
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        except Exception as e:
            LOG.error(f"Commit transactions error: {e}")
            await session.rollback()


async def process_pending_payments() -> None:
    async with get_session() as session:
        redis_client = await get_redis()
        manager = PaymentManager(session, redis_client)
        pendings = await manager.get_pending_payments(PaymentMethod.TON)
        
        for payment in pendings:
            try:
                await manager.check_payment(payment['id'])
            except Exception as e:
                LOG.error(f"Check payment error: {e}")


async def mark_failed_payments() -> None:
    async with get_session() as session:
        redis_client = await get_redis()
        manager = PaymentManager(session, redis_client)
        try:
            await manager.payment_repo.mark_failed_old_payments()
        except Exception as e:
            LOG.error(f"Mark failed payments error: {e}")


async def check_ton_transactions() -> None:
    try:
        tonapi = AsyncTonapi(api_key=env.TONAPI_KEY)
        
        txs = await fetch_new_transactions(tonapi)
        await insert_transactions(txs)
        await process_pending_payments()
        await mark_failed_payments()
        
    except Exception as e:
        LOG.error(f"TON transactions check error: {type(e).__name__}: {e}")