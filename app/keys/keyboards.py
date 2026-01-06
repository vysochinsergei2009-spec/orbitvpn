from typing import Callable, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.settings.config import env, PLANS


def btn(text: str, callback: str) -> dict:
    return {'text': text, 'callback_data': callback}


def url_btn(text: str, url: str) -> dict:
    return {'text': text, 'url': url}


def _build(buttons: list[dict], adjust: int | list[int] = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for b in buttons:
        if 'url' in b:
            builder.button(text=b['text'], url=b['url'])
        elif 'switch_inline_query' in b:
            builder.button(text=b['text'], switch_inline_query=b['switch_inline_query'])
        else:
            builder.button(text=b['text'], callback_data=b['callback_data'])
    
    if isinstance(adjust, int):
        builder.adjust(adjust)
    else:
        builder.adjust(*adjust)
    
    return builder.as_markup()



def main_kb(t: Callable, user_id: int = None) -> InlineKeyboardMarkup:
    buttons = [
        btn(t('my_vpn'), 'myvpn'),
        btn(t('balance'), 'balance'),
        btn(t('settings'), 'settings'),
    ]
    
    if user_id and user_id in env.ADMIN_TG_IDS:
        buttons.append(btn(t('admin'), 'admin_panel'))
    else:
        buttons.append(url_btn(t('help'), 'https://t.me/chnddy'))
    
    return _build(buttons, [1, 1, 2])


def balance_kb(t: Callable, show_renew: bool = False) -> InlineKeyboardMarkup:
    buttons = [btn(t('add_funds'), 'add_funds')]
    
    if show_renew:
        buttons.append(btn(t('renew_subscription_btn'), 'renew_subscription'))
    
    buttons.append(btn(t('back_main'), 'back_main'))
    return _build(buttons)


def myvpn_kb(t: Callable, configs: list[dict], has_active_sub: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    
    if not configs:
        buttons.append(btn(
            t('add_config' if has_active_sub else 'buy_sub'),
            'add_config' if has_active_sub else 'buy_sub'
        ))
    
    for i, cfg in enumerate(configs, 1):
        display_name = cfg.get('name') or f"{t('config')} {i}"
        buttons.append(btn(display_name, f"cfg_{cfg['id']}"))
    
    if has_active_sub or configs:
        buttons.append(btn(t('extend'), 'renew_subscription'))
    
    buttons.append(btn(t('back_main'), 'back_main'))
    return _build(buttons)


def actions_kb(t: Callable, cfg_id: int = None) -> InlineKeyboardMarkup:
    delete_cb = f"delete_cfg_{cfg_id}" if cfg_id else "delete_config"
    qr_cb = f"qr_cfg_{cfg_id}" if cfg_id else "qr_config"
    
    return _build([
        btn(t('delete_config'), delete_cb),
        btn(t('qr_code'), qr_cb),
        btn(t('back'), 'myvpn'),
    ], adjust=2)


def sub_kb(t: Callable, is_extension: bool = False) -> InlineKeyboardMarkup:
    monthly_price = PLANS['sub_1m']['price']
    buttons = []
    
    for key, plan in PLANS.items():
        if not key.startswith('sub_'):
            continue
        
        months = plan['days'] // 30
        regular_cost = monthly_price * months
        savings = regular_cost - plan['price']
        savings_percent = int((savings / regular_cost) * 100) if regular_cost > 0 else 0
        
        base_text = t(f'extend_by_{key.split("_")[1]}' if is_extension else key).format(price=plan['price'])
        
        if months >= 3 and savings_percent > 0:
            text = f"{base_text} 💰(-{savings_percent}%)"
        else:
            text = base_text
        
        buttons.append(btn(text, key))
    
    buttons.append(btn(t('back_main'), 'back_main'))
    return _build(buttons)


def set_kb(t: Callable) -> InlineKeyboardMarkup:
    return _build([
        btn(t('referral'), 'referral'),
        btn(t('notifications'), 'notifications_settings'),
        btn(t('change_language'), 'change_lang'),
        btn(t('back_main'), 'back_main'),
    ])


def get_language_keyboard(t: Callable) -> InlineKeyboardMarkup:
    return _build([
        btn('🇺🇸 English', 'set_lang:en'),
        btn('🇷🇺 Русский', 'set_lang:ru'),
        btn(t('back'), 'settings'),
    ])


def get_notifications_keyboard(t: Callable) -> InlineKeyboardMarkup:
    return _build([
        btn(t('toggle_notifications'), 'toggle_notifications'),
        btn(t('back'), 'settings'),
    ])


def get_payment_methods_keyboard(t: Callable) -> InlineKeyboardMarkup:
    return _build([
        btn('TON', 'select_method_ton'),
        btn(t('pm_stars'), 'select_method_stars'),
        btn('CryptoBot (USDT)', 'select_method_cryptobot'),
        btn('YooKassa (RUB)', 'select_method_yookassa'),
        btn(t('back'), 'balance'),
    ], adjust=1)


def get_payment_amounts_keyboard(t: Callable, method: str) -> InlineKeyboardMarkup:
    return _build([
        btn('200 RUB', f'amount_{method}_200'),
        btn('500 RUB', f'amount_{method}_500'),
        btn('1000 RUB', f'amount_{method}_1000'),
        btn(t('custom_amount'), f'amount_{method}_custom'),
        btn(t('back'), 'add_funds'),
    ], adjust=[3, 1, 1])


def get_referral_keyboard(t: Callable, ref_link: str) -> InlineKeyboardMarkup:
    return _build([
        {'text': t('share'), 'switch_inline_query': ref_link},
        btn(t('back'), 'back_main'),
    ])


def qr_delete_kb(t: Callable) -> InlineKeyboardMarkup:
    return _build([btn(t('delete_config'), 'delete_qr_msg')])


def balance_button_kb(t: Callable) -> InlineKeyboardMarkup:
    return _build([btn(t('balance'), 'balance')])


def back_balance(t: Callable) -> InlineKeyboardMarkup:
    return _build([btn(t('back'), 'balance')])


def get_renewal_notification_keyboard(t: Callable) -> InlineKeyboardMarkup:
    return _build([
        btn(t('renew_now'), 'renew_subscription'),
        btn(t('balance'), 'balance'),
    ], adjust=2)


def payment_success_actions(t: Callable, has_active_sub: bool) -> InlineKeyboardMarkup:
    if has_active_sub:
        return _build([
            btn(t('extend'), 'renew_subscription'),
            btn(t('back_main'), 'back_main'),
        ])
    return _build([
        btn(t('buy_sub'), 'buy_sub'),
        btn(t('back_main'), 'back_main'),
    ])



