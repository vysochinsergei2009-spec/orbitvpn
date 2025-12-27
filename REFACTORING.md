# Project Refactoring - Structure Reorganization

## Дата: 27 декабря 2025

## Цель рефакторинга
Структурировать проект подобно `vendor/app/`, сделав его более логичным и понятным.

---

## Изменения в структуре

### ✅ Создано:

#### 1. **`app/routers/`** - все хэндлеры (роутеры)
```
app/routers/
├── __init__.py          # Единый роутер для всего бота
├── utils.py             # Утилиты для роутеров
├── admin/               # Админские хэндлеры
│   ├── __init__.py
│   ├── broadcast.py
│   ├── panel.py
│   ├── payments.py
│   ├── servers.py
│   └── users.py
└── user/                # Пользовательские хэндлеры
    ├── __init__.py
    ├── admin/
    ├── billing/
    ├── servers/
    └── users/
```

#### 2. **`app/keys/`** - все клавиатуры
```
app/keys/
├── admin.py             # Админские клавиатуры
└── ...                  # Пользовательские клавиатуры
```

#### 3. **`app/middleware/`** - все middleware
```
app/middleware/
├── __init__.py
└── admin.py             # AdminMiddleware
```

---

### ❌ Удалено:

1. **`app/admin/`** → разделено на:
   - `app/routers/admin/` - хэндлеры
   - `app/keys/admin.py` - клавиатуры
   - `app/middleware/admin.py` - middleware

2. **`app/core/handlers/`** → `app/routers/user/`

3. **`app/repo/`** → `app/db/` (было сделано ранее)

---

## Изменения в импортах

### Главные изменения:

```python
# Старое → Новое

from app.admin.keyboards import ... → from app.keys.admin import ...
from app.admin.middleware import ... → from app.middleware.admin import ...
from app.core.handlers import router → from app.routers import router
from app.core.handlers.utils import ... → from app.routers.utils import ...
from app.repo. import ... → from app.db. import ...
```

### Файл `run.py`:
```python
# Было:
from app.core.handlers import router
from app.repo.db import close_db
from app.repo.init_db import init_database

# Стало:
from app.routers import router  # Единый роутер
from app.db.db import close_db
from app.db.init_db import init_database
```

---

## Итоговая структура `app/`

```
app/
├── api/              # API клиенты
├── db/               # База данных (было repo/)
├── keys/             # Все клавиатуры
│   ├── admin.py
│   └── ...
├── middleware/       # Все middleware
│   ├── __init__.py
│   └── admin.py
├── models/           # Модели данных
├── payments/         # Платежные системы
├── routers/          # Все хэндлеры
│   ├── __init__.py   # Единый роутер
│   ├── utils.py
│   ├── admin/        # Админские роутеры
│   └── user/         # Пользовательские роутеры
├── settings/         # Настройки
└── utils/            # Утилиты
```

---

## Преимущества новой структуры

1. **Логичное разделение**:
   - Хэндлеры → `app/routers/`
   - Клавиатуры → `app/keys/`
   - Middleware → `app/middleware/`

2. **Единый точка входа**:
   - Все роутеры собираются в `app/routers/__init__.py`
   - Простой импорт в `run.py`: `from app.routers import router`

3. **Лучшая масштабируемость**:
   - Легко добавлять новые роутеры
   - Легко находить нужный код

4. **Согласованность с vendor/**:
   - Структура теперь похожа на `vendor/app/`

---

## Коммиты

Все изменения разбиты на логические коммиты:

1. `[Refactor] Create app/middleware/ and move admin keyboards to app/keys/`
2. `[Refactor] Create app/routers/admin/ - part 1 (panel, broadcast)`
3. `[Refactor] Create app/routers/admin/ - part 2 (servers, payments, users)`
4. `[Refactor] Create unified router in app/routers/__init__.py`
5. `[Refactor] Update run.py imports - use unified router from app.routers`

---

## Тестирование

Чтобы проверить что всё работает:

1. Запусти бота: `python run.py`
2. Проверь основные команды: `/start`, админ-панель
3. Убедись что нет ошибок импорта

---

## Следующие шаги (опционально)

1. Добавить type hints в все функции
2. Создать юнит-тесты для роутеров
3. Добавить docstrings ко всем модулям
4. Настроить pre-commit hooks (линтеры, форматтеры)
