import logging
from decimal import Decimal
from typing import Optional
from aiocryptopay import AioCryptoPay, Networks
from app.payments.gateway.base import BasePaymentGateway
from app.payments.models import PaymentResult, PaymentMethod
from app.repo.payments import PaymentRepository
from app.utils.rates import get_usdt_rub_rate
from config import CRYPTOBOT_TOKEN, CRYPTOBOT_TESTNET

LOG = logging.getLogger(__name__)


class CryptoBotGateway(BasePaymentGateway):
    requires_polling = True

    def __init__(self, session, redis_client=None):
        self.session = session
        self.payment_repo = PaymentRepository(session, redis_client)
        self._cryptopay: Optional[AioCryptoPay] = None

    async def _get_cryptopay(self) -> AioCryptoPay:
        if self._cryptopay is None:
            if not CRYPTOBOT_TOKEN:
                raise ValueError("CRYPTOBOT_TOKEN is not configured in .env")

            network = Networks.TEST_NET if CRYPTOBOT_TESTNET else Networks.MAIN_NET
            self._cryptopay = AioCryptoPay(token=CRYPTOBOT_TOKEN, network=network)

        return self._cryptopay

    async def create_payment(
        self,
        t,
        tg_id: int,
        amount: Decimal,
        chat_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> PaymentResult:
        """Create CryptoBot invoice"""
        if payment_id is None:
            raise ValueError("payment_id is required for CryptoBot")

        try:
            cryptopay = await self._get_cryptopay()

            # Get current USDT/RUB exchange rate
            usdt_rate = await get_usdt_rub_rate()

            # Convert RUB to USDT
            usdt_amount = amount / usdt_rate

            LOG.info(f"Converting {amount} RUB to {usdt_amount:.2f} USDT (rate: {usdt_rate})")

            # Get bot username for callback URL
            profile = await cryptopay.get_me()
            bot_username = profile.payment_processing_bot_username

            invoice = await cryptopay.create_invoice(
                asset='USDT',
                amount=float(usdt_amount),  # Amount in USDT after conversion from RUB
                description=comment or f"Payment #{payment_id}",
                paid_btn_name="callback",  # Button to return to bot after payment
                paid_btn_url=f"https://t.me/{bot_username}",
                payload=str(payment_id),  # Used to identify payment in webhook
                allow_comments=False,
                allow_anonymous=False,
            )

            # Store invoice_id in payment metadata
            await self.payment_repo.update_payment_metadata(
                payment_id=payment_id,
                metadata={'invoice_id': invoice.invoice_id}
            )

            pay_url = invoice.bot_invoice_url

            text = (
                t("cryptobot_payment_intro") + "\n\n"
                + t("cryptobot_amount", amount=amount) + "\n"
                + f"≈ {usdt_amount:.2f} USDT\n\n"
                + t("cryptobot_click_button")
            )

            return PaymentResult(
                payment_id=payment_id,
                method=PaymentMethod.CRYPTOBOT,
                amount=amount,
                text=text,
                pay_url=pay_url,
                invoice_id=invoice.invoice_id
            )

        except Exception as e:
            LOG.error(f"Error creating CryptoBot invoice: {e}")
            raise ValueError(f"Failed to create CryptoBot invoice: {e}")

    async def check_payment(self, payment_id: int) -> bool:
        """Check if CryptoBot invoice has been paid"""
        try:
            payment = await self.payment_repo.get_payment(payment_id)
            if not payment:
                LOG.warning(f"Payment {payment_id} not found")
                return False

            extra_data = payment.get('extra_data', {})
            invoice_id = extra_data.get('invoice_id') if extra_data else None

            if not invoice_id:
                LOG.debug(f"CryptoBot payment {payment_id} has no invoice_id")
                return False

            cryptopay = await self._get_cryptopay()

            # Get invoice status from CryptoBot
            invoices = await cryptopay.get_invoices(invoice_ids=[invoice_id])

            if not invoices:
                LOG.warning(f"CryptoBot invoice {invoice_id} not found")
                return False

            invoice = invoices[0]

            # Check if invoice is paid
            if invoice.status == 'paid':
                # Update payment status
                tx_hash = f"cryptobot_{invoice_id}"
                await self.payment_repo.update_payment_status(payment_id, "confirmed", tx_hash)
                await self.on_payment_confirmed(payment_id, tx_hash)
                LOG.info(f"CryptoBot payment confirmed: id={payment_id}, invoice={invoice_id}")
                return True

            return False

        except Exception as e:
            LOG.error(f"Error checking CryptoBot payment {payment_id}: {e}")
            return False

    async def on_payment_confirmed(self, payment_id: int, tx_hash: Optional[str] = None):
        """Callback when payment is confirmed"""
        LOG.info(f"CryptoBot payment confirmed callback: id={payment_id}, tx={tx_hash}")

    async def close(self):
        """Close CryptoPay client session"""
        if self._cryptopay:
            await self._cryptopay.close()
