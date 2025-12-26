# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OrbitVPN is a production Telegram bot for managing VPN subscriptions built with:
- **aiogram 3.22.0** - Modern async Telegram bot framework with FSM support
- **PostgreSQL + asyncpg** - Relational database with SQLAlchemy 2.x ORM
- **Redis** - High-performance caching layer for user data and rate limiting
- **Marzban** - Multi-instance VPN panel integration with load balancing
- **Payment Gateways** - TON cryptocurrency, Telegram Stars, and CryptoBot (all optional)

The bot provides:
- User authentication with referral system (50 RUB bonus)
- Free 7-day trial for new users
- Subscription management (1M, 3M, 6M, 12M plans)
- VPN configuration creation with automatic load balancing
- Multi-language support (Russian/English)
- Payment processing with automatic confirmation
- Rate limiting and anti-spam protection

## Running the Application

### Start/Stop Commands
```bash
# Start the bot (mentioned in README)
boton.sh

# Stop the bot (mentioned in README)
botoff.sh

# Direct run (for development)
python3 run.py
```

### Environment Setup
Create a `.env` file with required credentials:

**Required Variables:**
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`, `DATABASE_HOST` - PostgreSQL connection credentials
- `TON_ADDRESS` - Wallet address for TON cryptocurrency payments
- `TONAPI_URL` - TON API endpoint (e.g., https://tonapi.io)
- `TONAPI_KEY` - TON API authentication key
- `S001_MARZBAN_USERNAME`, `S001_MARZBAN_PASSWORD`, `S001_BASE_URL` - Primary Marzban instance credentials (backward compatibility)

**Optional Variables:**
- `REDIS_URL` - Redis connection string (default: `redis://localhost`)
- `CRYPTOBOT_TOKEN` - CryptoBot payment gateway token (if using CryptoBot)
- `CRYPTOBOT_TESTNET` - Set to "true" for testnet mode (default: false)
- `MAX_IPS_PER_CONFIG` - Max concurrent devices per VPN config (default: 2)
- `SUB_1M_PRICE`, `SUB_3M_PRICE`, `SUB_6M_PRICE`, `SUB_12M_PRICE` - Override subscription prices from plans.json

**Multi-Instance Marzban:**
For production deployments with multiple Marzban servers, add instances via database:
```sql
INSERT INTO marzban_instances (id, name, base_url, username, password, is_active, priority, excluded_node_names)
VALUES ('s002', 'Secondary Server', 'https://s002.example.com:8000/', 'admin', 'password', TRUE, 90, ARRAY['node_slow']);
```

### Dependencies
Install with: `pip install -r requirements.txt`

## Architecture

### Entry Point
- `run.py` - Main entry point that initializes the bot, dispatcher, middlewares (locale, rate limiting), and starts polling

### Core Components

**app/core/handlers/** - Modular handler system with aiogram routers
- `auth.py` - User authentication, /start command, referral link processing
- `configs.py` - VPN configuration CRUD operations, subscription validation
- `payments.py` - Payment flow orchestration (TON, Stars, CryptoBot), balance management, FSM states
- `subscriptions.py` - Subscription plan purchase, renewal, expiry checks
- `settings.py` - User preferences, language switching
- `utils.py` - Shared utilities (safe_get_repo, error handling, callback validators)
- `__init__.py` - Router aggregation and registration

**app/core/keyboards.py** - Dynamic inline keyboard layouts with localization support

**app/repo/** - Repository pattern with async database access
- `base.py` - BaseRepository abstract class with Redis caching methods
- `db.py` - SQLAlchemy async engine, session factory, database lifecycle
- `init_db.py` - Database initialization and table creation
- `models.py` - SQLAlchemy ORM models:
  - `User` - User accounts with balance, subscription, referral tracking
  - `Config` - VPN configurations linked to users and Marzban instances
  - `Payment` - Payment transaction records (status, method, amount)
  - `TonTransaction` - TON blockchain transaction tracking
  - `Promocode` - Promotional codes with usage limits
  - `Referral` - Referral relationships and bonus tracking
  - `MarzbanInstance` - Multi-instance VPN panel registry
  - `Server` - **DEPRECATED** (legacy single-server model)
- `user.py` - UserRepository with extensive Redis caching (balance, configs, subscription)
- `payments.py` - PaymentRepository for transaction CRUD operations
- `marzban_client.py` - **PRIMARY**: Multi-instance Marzban API client with intelligent load balancing
- `server.py` - **DEPRECATED**: Legacy ServerRepository (replaced by marzban_client.py)

**app/payments/** - Pluggable payment gateway system
- `manager.py` - PaymentManager: factory pattern for payment creation and confirmation
- `models.py` - Pydantic models (PaymentMethod enum, PaymentResult, transaction DTOs)
- `gateway/base.py` - BasePaymentGateway abstract interface
- `gateway/ton.py` - TonGateway: TON cryptocurrency with blockchain polling
- `gateway/stars.py` - TelegramStarsGateway: Telegram Stars in-app purchases
- `gateway/cryptobot.py` - CryptoBotGateway: CryptoBot payment processor (optional)

**app/utils/** - Shared utilities and background tasks
- `redis.py` - Redis client initialization, connection pooling
- `rate_limit.py` - RateLimitMiddleware: token-bucket rate limiting with Redis backend
- `logging.py` - Structured logging configuration with log level control
- `updater.py` - TonTransactionsUpdater: background task for blockchain payment polling
- `payment_cleanup.py` - PaymentCleanupTask: periodic cleanup of old payment records
- `rates.py` - Cryptocurrency exchange rate fetching (TON/RUB, USD/RUB)

**app/locales/** - Internationalization (i18n)
- `locales.py` - Translation dictionaries for Russian (ru) and English (en)
- `locales_mw.py` - LocaleMiddleware: automatic language detection from user settings

### Configuration Files
- `config.py` - Central configuration with validation, environment variable loading, constants
- `plans.json` - Subscription plan definitions (duration in days, prices in RUB)
- `.env` - Environment variables (not in version control, see `.env.example`)
- `boton.sh` - Production startup script with process management
- `botoff.sh` - Graceful shutdown script
- `bot_manager.py` - Process manager for bot lifecycle

## Key Architectural Patterns

### Repository Pattern
All database access follows the repository pattern with `BaseRepository`:
- **Async SQLAlchemy ORM** for type-safe queries
- **Redis caching layer** with automatic invalidation
- **Session management** via context managers
- **Error handling** with transaction rollback

Key methods in BaseRepository:
- `get_cached(key: str)` - Retrieve from Redis cache
- `set_cache(key: str, value: Any, ttl: int)` - Store in cache with expiration
- `delete_cache(key: str)` - Invalidate cache entry
- `invalidate_pattern(pattern: str)` - Bulk cache invalidation

### Redis Caching Strategy
Performance-critical data is cached with strategic TTLs:

**User Data:**
- `user:{tg_id}:balance` - Current balance (TTL: 300s)
- `user:{tg_id}:configs` - List of user VPN configs (TTL: 300s)
- `user:{tg_id}:sub_end` - Subscription expiry timestamp (TTL: 300s)
- `user:{tg_id}:active_sub` - Active subscription status (TTL: 300s)

**System Data:**
- `servers:best` - Best available Marzban server by load (TTL: 120s)
- `marzban:{instance_id}:token` - Marzban auth tokens (TTL: dynamic)
- `rate_limit:{user_id}:{action}` - Rate limiting buckets (TTL: 3600s)

**Cache Invalidation:**
- Payment confirmation → Invalidate balance cache
- Config creation/deletion → Invalidate user configs cache
- Subscription purchase → Invalidate subscription caches

### Payment Flow
Payment processing follows a gateway-agnostic pattern:

**1. Initiation:**
- User clicks "Add Funds" → Selects payment method (TON/Stars/CryptoBot)
- Handler validates amount and creates Payment record in database
- PaymentManager dispatches to appropriate gateway

**2. Gateway-Specific Processing:**

**TON Cryptocurrency:**
- Generate unique payment comment (payment ID)
- Display wallet address and comment to user
- TonTransactionsUpdater polls TON blockchain every 30s
- On matching transaction: confirm payment, credit balance
- Payment expires after 10 minutes if not completed

**Telegram Stars:**
- Create Telegram invoice via Bot API
- User proceeds to in-app payment
- Bot receives `pre_checkout_query` → validate payment
- Bot receives `successful_payment` → confirm and credit balance

**CryptoBot (Optional):**
- Generate payment invoice via CryptoBot API
- User completes payment on CryptoBot platform
- Webhook confirms payment → credit balance

**3. Confirmation:**
- Update Payment status to "confirmed"
- Increment user balance in database
- Invalidate Redis cache for user balance
- Send confirmation message to user

**4. Cleanup:**
- PaymentCleanupTask removes payments older than 7 days
- Prevents database bloat from expired/failed payments

### VPN Config Management (Multi-Instance Load Balancing)
The bot supports multiple Marzban VPN panels with intelligent load distribution:

**1. Config Creation Flow:**
- User clicks "Add Config" → System validates active subscription
- Check user hasn't exceeded max configs for subscription tier
- MarzbanClient selects optimal server and node

**2. Load Balancing Algorithm (MarzbanClient):**
```
For each active MarzbanInstance:
  - Authenticate and fetch auth token (cached in Redis)
  - Retrieve all nodes from instance
  - Filter out nodes in excluded_node_names array
  - Calculate load score: users_count * usage_coefficient + traffic_weight
  - Track best node across all instances

Select node with lowest load score
```

**3. Config Provisioning:**
- Create Marzban user with unique username
- Set data limit, expiry based on subscription
- Generate VLESS/Vmess link with node inbounds
- Store Config record with instance_id and Marzban username
- Return subscription link to user

**4. Config Management:**
- **View Configs:** Display all user configs with expiry, traffic stats
- **Delete Config:** Remove from database + delete Marzban user via API
- **Auto-Expiry:** Configs inherit subscription end date

**5. Multi-Instance Benefits:**
- Horizontal scaling across multiple VPN servers
- Geographic distribution for better latency
- Fault tolerance (if one instance fails, others handle traffic)
- Node exclusion for maintenance (add to excluded_node_names array)

**6. Migration from Legacy System:**
- Old `Server` model deprecated
- Existing configs remain functional
- New configs use multi-instance system automatically

### Middleware Stack
Middlewares are applied to both `message` and `callback_query` updates in run.py:

**1. LocaleMiddleware** (First)
- Detects user language preference from database
- Injects translation dictionary into handler context
- Falls back to Russian if user language not set
- Enables `t()` function for localized strings

**2. RateLimitMiddleware** (Second)
- Token-bucket rate limiting with Redis backend
- Different limits per action:
  - `/start`: 3 seconds between calls
  - `add_funds`, payment methods: 5-10 seconds
  - Subscription purchases: 2-3 seconds
  - Default: 0.8 seconds for other actions
- Returns localized "too many requests" message
- Automatic cleanup task runs hourly to remove expired buckets

## Development Notes

### Logging Configuration
Set in config.py:
- `IS_LOGGING = True` - Enable/disable logging
- `LOG_LEVEL = "DEBUG"` - Set to "INFO", "DEBUG", or "ERROR"
- `LOG_AIOGRAM = False` - Toggle aiogram library logging

### Constants
- `FREE_TRIAL_DAYS = 7` - Free trial duration for new users
- `REFERRAL_BONUS = 50.0` - Bonus RUB for referrals
- `REDIS_TTL = 300` - Default Redis cache TTL (5 minutes)
- `TELEGRAM_STARS_RATE = 1.35` - Stars to RUB conversion
- `TON_RUB_RATE = 220` - TON to RUB rate (may be dynamic via rates.py)
- `PAYMENT_TIMEOUT_MINUTES = 10` - Payment expiration window

### State Management
FSM states defined in handlers.py:
- `PaymentState.waiting_amount` - Awaiting payment amount input
- `PaymentState.method` - Awaiting payment method selection

### Error Handling
- Handlers catch exceptions and log via `LOG.error()` with context
- User-facing errors return localized messages via translation keys
- Payment failures tracked with status: "pending", "confirmed", "failed"
