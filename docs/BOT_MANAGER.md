# Bot Manager - CLI для управления OrbitVPN ботом

Красивый терминальный интерфейс для управления ботом и его кэшем.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Использование

```bash
python bot_manager.py [COMMAND]
```

### Основные команды

#### Показать информацию о боте
```bash
python bot_manager.py info
```
Показывает конфигурацию бота, планы подписок, настройки БД и Redis.

---

## Cache Management (Управление кэшем)

### Очистить Telegraph кэш (инструкции установки)
```bash
python bot_manager.py cache telegraph
```
**Использовать когда:** обновили HTML-шаблоны инструкций и хотите пересоздать Telegraph страницы.

### Показать статистику кэша
```bash
python bot_manager.py cache stats
```
Показывает:
- Общее количество ключей
- Hit rate (процент попаданий в кэш)
- Распределение ключей по префиксам

### Очистить кэш пользователей
```bash
python bot_manager.py cache users
```
Удаляет весь кэш пользователей (баланс, конфиги, подписки). Потребует подтверждения.

### Очистить кэш по паттерну
```bash
# Все ключи
python bot_manager.py cache clear

# Конкретный паттерн
python bot_manager.py cache clear -p "user:*:balance"

# Без подтверждения
python bot_manager.py cache clear -p "telegraph:*" --no-confirm
```

---

## Примеры использования

### После обновления инструкции по установке
```bash
# 1. Отредактировали install_ru.html / install_en.html
# 2. Очищаем Telegraph кэш
python bot_manager.py cache telegraph
# 3. Готово! При следующем запросе создастся новая страница
```

### Проверка производительности кэша
```bash
python bot_manager.py cache stats
```
Если Hit rate < 80% - возможно стоит увеличить TTL в config.py

### Полная очистка кэша (редко нужно)
```bash
python bot_manager.py cache clear
# Подтвердить удаление всех ключей
```

---

## Справка по командам

```bash
# Список всех команд
python bot_manager.py --help

# Справка по cache
python bot_manager.py cache --help

# Справка по конкретной команде
python bot_manager.py cache clear --help
```

---

## Алиас для удобства (опционально)

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
alias botmanager='python /root/orbitvpn/bot_manager.py'
```

Использование после добавления алиаса:
```bash
botmanager cache telegraph
botmanager info
botmanager cache stats
```
