from decimal import Decimal

from aiogram import Router, F
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from app.core.keyboards import (
    balance_kb, get_payment_methods_keyboard, get_payment_amounts_keyboard,
    back_balance, payment_success_actions
)
from app.repo.db import get_session
from app.payments.manager import PaymentManager
from app.payments.models import PaymentMethod
from app.utils.logging import get_logger
from app.utils.redis import get_redis
from config import TELEGRAM_STARS_RATE, PLANS, bot
from .utils import safe_answer_callback, get_repositories, get_user_balance, format_expire_date

router = Router()
LOG = get_logger(__name__)


class PaymentState(StatesGroup):
    waiting_custom_amount = State()


@router.callback_query(F.data == 'balance')
async def balance_callback(callback: CallbackQuery, t, state: FSMContext):
    await safe_answer_callback(callback)
    await state.clear()
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _, _ = await get_repositories(session)
        balance = await get_user_balance(user_repo, tg_id)
        has_active_sub = await user_repo.has_active_subscription(tg_id)

        text = t('balance_text', balance=balance)

        if has_active_sub:
            sub_end = await user_repo.get_subscription_end(tg_id)
            expire_date = format_expire_date(sub_end)
            text += f"\n\n{t('subscription_active_until', expire_date=expire_date)}"
        else:
            cheapest = min(PLANS.values(), key=lambda x: x['price'])
            text += f"\n\n{t('subscription_from', price=cheapest['price'])}"

        await callback.message.edit_text(text, reply_markup=balance_kb(t))


@router.callback_query(F.data == 'add_funds')
async def add_funds_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    await callback.message.edit_text(
        t('payment_method'),
        reply_markup=get_payment_methods_keyboard(t)
    )


@router.callback_query(F.data.startswith('select_method_'))
async def select_payment_method(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    method = callback.data.replace('select_method_', '')
    await callback.message.edit_text(
        t('select_amount'),
        reply_markup=get_payment_amounts_keyboard(t, method)
    )


@router.callback_query(F.data.startswith('amount_'))
async def process_amount_selection(callback: CallbackQuery, t, state: FSMContext):
    await safe_answer_callback(callback)
    parts = callback.data.split('_')
    method_str = parts[1]
    amount_str = parts[2]

    if amount_str == 'custom':
        await state.set_state(PaymentState.waiting_custom_amount)
        await state.set_data({'method': method_str})
        await callback.message.edit_text(t('enter_amount'), reply_markup=back_balance(t))
        return

    await process_payment(callback, t, method_str, Decimal(amount_str))


@router.message(StateFilter(PaymentState.waiting_custom_amount))
async def process_custom_amount(message: Message, state: FSMContext, t):
    tg_id = message.from_user.id

    try:
        amount = Decimal(message.text)
        if amount < 200 or amount > 100000:
            raise ValueError("Amount out of range")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Too many decimal places")
    except (ValueError, TypeError) as e:
        LOG.error(f"Invalid amount from user {tg_id}: {message.text} - {e}")
        await message.answer(t('invalid_amount'))
        return

    data = await state.get_data()
    method_str = data.get('method')
    await state.clear()

    await process_payment(message, t, method_str, amount)


async def process_payment(msg_or_callback, t, method_str: str, amount: Decimal):
    tg_id = msg_or_callback.from_user.id
    is_callback = isinstance(msg_or_callback, CallbackQuery)

    try:
        method = PaymentMethod(method_str)
    except ValueError:
        LOG.error(f"Invalid method for user {tg_id}: {method_str}")
        text = t('error_creating_payment')
        if is_callback:
            await msg_or_callback.message.edit_text(text, reply_markup=balance_kb(t))
        else:
            await msg_or_callback.answer(text)
        return

    async with get_session() as session:
        try:
            redis_client = await get_redis()
            manager = PaymentManager(session, redis_client)
            chat_id = msg_or_callback.message.chat.id
            result = await manager.create_payment(t, tg_id=tg_id, method=method, amount=amount, chat_id=chat_id)

            if method == PaymentMethod.TON:
                text = t(
                    'ton_payment_instruction',
                    ton_amount=f'<b>{result.expected_crypto_amount} TON</b>',
                    wallet=f"<pre><code>{result.wallet}</code></pre>",
                    comment=f'<pre>{result.comment}</pre>'
                )
                if is_callback:
                    await msg_or_callback.message.edit_text(text, parse_mode="HTML")
                else:
                    await msg_or_callback.answer(text, parse_mode="HTML")

            elif method == PaymentMethod.STARS and result.url:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=t('pay_button'), url=result.url)]
                ])
                if is_callback:
                    await msg_or_callback.message.edit_text(result.text, reply_markup=kb)
                else:
                    await msg_or_callback.answer(result.text, reply_markup=kb)

        except Exception as e:
            LOG.error(f"Payment error for user {tg_id}: {type(e).__name__}: {e}")
            text = t('error_creating_payment')
            if is_callback:
                await msg_or_callback.message.edit_text(text, reply_markup=balance_kb(t))
            else:
                await msg_or_callback.answer(text)


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    payload = pre_checkout_query.invoice_payload

    if not payload.startswith("topup_"):
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="Invalid payment format"
        )
        return

    try:
        parts = payload.split("_")
        if len(parts) != 3:
            raise ValueError("Invalid payload structure")
        tg_id = int(parts[1])
        amount = int(parts[2])

        if tg_id != pre_checkout_query.from_user.id:
            LOG.warning(f"User {pre_checkout_query.from_user.id} tried to pay for user {tg_id}")
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Invalid payment recipient"
            )
            return

        if amount < 200 or amount > 100000:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Invalid payment amount"
            )
            return

        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )

    except (ValueError, IndexError) as e:
        LOG.error(f"Pre-checkout validation failed for payload {payload}: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="Invalid payment data"
        )


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, t):
    tg_id = message.from_user.id
    payment_id = message.successful_payment.telegram_payment_charge_id
    stars_paid = message.successful_payment.total_amount
    rub_amount = Decimal(stars_paid) * Decimal(str(TELEGRAM_STARS_RATE))

    async with get_session() as session:
        user_repo, _, payment_repo = await get_repositories(session)

        if await payment_repo.mark_payment_processed_with_lock(payment_id, tg_id, rub_amount):
            await user_repo.change_balance(tg_id, rub_amount)

            has_active_sub = await user_repo.has_active_subscription(tg_id)

            await message.answer(
                t('payment_success', amount=float(rub_amount)),
                reply_markup=payment_success_actions(t, has_active_sub)
            )
        else:
            await message.answer(t('payment_already_processed'))
