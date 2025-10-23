# Handlers Module Structure

Handlers are organized by domain for better code organization and maintainability.

## Module Overview

| Module | Lines | Handlers | Description |
|--------|-------|----------|-------------|
| `auth.py` | 51 | 3 | User authentication, registration, referral system |
| `configs.py` | 139 | 5 | VPN config management (create, view, delete, QR) |
| `subscriptions.py` | 89 | 3 | Subscription purchases and renewals |
| `payments.py` | 231 | 8 | Balance top-ups (TON, Telegram Stars) |
| `settings.py` | 41 | 3 | User settings and language preferences |
| `utils.py` | 76 | - | Shared helper functions |
| `__init__.py` | 18 | - | Router aggregation |

## Handlers by Module

### auth.py
- `/start` - User registration with referral support
- `back_main` - Return to main menu
- `referral` - Show referral link and stats

### configs.py
- `myvpn` - List user VPN configurations
- `add_config` - Create new VPN config
- `cfg_*` - View specific config details
- `delete_cfg_*` - Delete VPN config
- `qr_cfg_*` - Generate QR code for config

### subscriptions.py
- `buy_sub` - Show subscription plans
- `sub_1m/3m/6m/12m` - Purchase specific plan
- `renew_subscription` - Extend existing subscription

### payments.py
- `balance` - View current balance
- `add_funds` - Select payment method
- `select_method_*` - Choose TON or Stars
- `amount_*` - Select or enter amount
- `process_custom_amount` - Handle custom amount input (FSM)
- `pre_checkout` - Validate Telegram Stars payment
- `successful_payment` - Process completed payment

### settings.py
- `settings` - Show settings menu
- `change_lang` - Language selection
- `set_lang:*` - Apply language change

## Design Principles

1. **Single Responsibility** - Each module handles one domain
2. **No Comments** - Code is self-documenting
3. **Shared Utilities** - Common functions in `utils.py`
4. **Consistent Error Handling** - All exceptions logged and user-friendly messages shown
5. **Clean Imports** - Only necessary imports per file

## Migration Notes

- Old `handlers.py` (595 lines) → New structure (645 lines across 7 files)
- Removed unused imports (`TON_RUB_RATE`, `server_repo`)
- Removed obsolete comments ("NEW: No longer need...")
- No functional changes - pure refactoring
