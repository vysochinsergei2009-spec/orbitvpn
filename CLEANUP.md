● Проанализировал проект. Нашел несколько категорий файлов и компонентов, которые можно почистить:

  1. DEPRECATED компоненты (можно удалить после миграции)

  app/repo/server.py - DEPRECATED
  - Помечен как устаревший в самом файле
  - Заменен на MarzbanClient
  - НЕ используется нигде в коде

  app/repo/models.py - класс Server (строки 79-95)
  - Модель базы данных помечена как DEPRECATED
  - Заменена на MarzbanInstance
  - Импортируется в user.py:11, но НЕ используется

  Рекомендация: Можно удалить только если:
  - В базе данных нет записей в таблице servers ИЛИ
  - Вы готовы сделать миграцию данных

  2. Неиспользуемые импорты

  app/repo/user.py:11
  from .models import User, Config, Server  # Server не используется!

  Исправление: Удалить Server из импорта:
  from .models import User, Config

  3. Бинарные файлы в репозитории

  libssl1.1_1.1.1f-1ubuntu2_amd64.deb (1.3 MB)
  - .deb файл в корне проекта
  - Не должен быть в Git репозитории

  Рекомендация: Удалить и добавить в .gitignore:
  rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb
  echo "*.deb" >> .gitignore

  4. Лог файлы

  bot.log (171 KB), logs/manager.log
  - Уже есть *.log в .gitignore, но файлы попали в репозиторий
  - Нужно удалить из Git

  Исправление:
  git rm --cached bot.log logs/manager.log

  5. Дополнительные директории (проверить необходимость)

  Найдены папки, которые могут быть частью другого компонента:

  - manager/ (448 KB) - Web dashboard manager
  - web/ (188 KB) - Web интерфейс
  - mac/ (592 KB) - MacOS приложение OrbitVPNManager
  - docs/ (88 KB) - Документация (YOOKASSA_SETUP.md, MANAGER_*.md и т.д.)
  - static/ (176 KB) - Статические файлы

  Вопрос: Используются ли эти компоненты в продакшене?
  - Если НЕТ - можно вынести в отдельный репозиторий
  - Если ДА - оставить как есть

  6. YooKassa Payment Gateway

  Статус: Полностью интегрирован и функционален
  - Файл: app/payments/gateway/yookassa.py
  - Конфиг: настроен в .env с реальными ключами
  - Зависимость: yookassa в requirements.txt

  НО: В CLAUDE.md упоминаются только TON, Stars, CryptoBot (YooKassa не задокументирован)

  Вопросы:
  1. Используется ли YooKassa в продакшене?
  2. Если нет - удалить gateway и убрать из PaymentManager
  3. Если да - добавить в документацию CLAUDE.md

  7. Обновить .gitignore

  Добавить игнорирование:
  # Binary files
  *.deb
  *.rpm

  # Logs (already there, but enforce)
  bot.log
  logs/*.log

  # OS specific
  .DS_Store
  *.swp

  ---
  Рекомендуемый план очистки

  Безопасные действия (можно делать сразу):
  1. Удалить импорт Server из app/repo/user.py:11
  2. Удалить libssl1.1_1.1.1f-1ubuntu2_amd64.deb
  3. Очистить логи из Git
  4. Обновить .gitignore

  Требует проверки:
  5. Удалить app/repo/server.py (если уверены, что не используется)
  6. Удалить класс Server из models.py и создать миграцию БД
  7. Решить судьбу YooKassa (оставить или удалить)
  8. Переместить manager/web/mac в отдельный репозиторий (если не используется)

  Хотите, чтобы я выполнил безопасные действия (пункты 1-4)?