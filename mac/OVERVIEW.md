# 📱 OrbitVPN Manager - Обзор

## Что создано

Полноценное **нативное macOS приложение** на **Swift + SwiftUI** для управления OrbitVPN ботом.

---

## 🎨 Дизайн приложения

### Архитектура
```
┌─────────────────────────────────────────┐
│     macOS App (Swift/SwiftUI)          │
│  ┌──────────────────────────────────┐  │
│  │   Views (SwiftUI)                │  │
│  │   - Dashboard, Services, Users   │  │
│  │   - Marzban, Broadcast, Logs     │  │
│  └──────────────────────────────────┘  │
│              ↕️ HTTP                    │
│  ┌──────────────────────────────────┐  │
│  │   Services                       │  │
│  │   - APIService (HTTP Client)     │  │
│  │   - BackendManager (Process)     │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
                ↕️
┌─────────────────────────────────────────┐
│  Python Backend (FastAPI)               │
│  - Auto-started by Swift app            │
│  - Runs on localhost:8080               │
│  - Manages bot services                 │
└─────────────────────────────────────────┘
```

---

## 📂 Структура файлов

```
mac/
├── README.md                      # Подробная документация
├── QUICKSTART.md                  # Быстрый старт (5 минут)
├── OVERVIEW.md                    # Этот файл
│
├── backend/                       # Python FastAPI backend (копия manager/)
│   ├── config/
│   ├── core/
│   ├── monitoring/
│   ├── services/
│   ├── utils/
│   └── web/
│       └── app.py                 # FastAPI приложение
│
└── OrbitVPNManager/               # Swift приложение
    ├── OrbitVPNManagerApp.swift  # Entry point
    ├── Info.plist                 # App metadata
    │
    ├── Models/
    │   └── Models.swift           # Data models (User, Service, Marzban)
    │
    ├── Services/
    │   ├── APIService.swift       # HTTP client для FastAPI
    │   └── BackendManager.swift   # Управление Python процессом
    │
    └── Views/
        ├── ContentView.swift      # Main window + sidebar
        ├── DashboardView.swift    # 📊 Главная статистика
        ├── ServicesView.swift     # 🖥️ Управление сервисами
        ├── UsersView.swift        # 👥 Пользователи
        ├── MarzbanView.swift      # 🌐 Marzban серверы
        ├── BroadcastView.swift    # 📢 Рассылки
        ├── LogsView.swift         # 📋 Логи в реальном времени
        └── SettingsView.swift     # ⚙️ Настройки
```

---

## 🎯 Функционал

### 1. Dashboard (📊 DashboardView)
```swift
// Что показывает:
- System Health (healthy/degraded)
- Services Running (3/4)
- Uptime (2d 5h)
- Total Users (1234)
- Active Subscriptions (567)
- Trial Users (123)
- New Today (45)
- Total Configs (890)

// Технологии:
- SwiftUI Charts для графиков (готово к добавлению)
- Async/await для загрузки данных
- Auto-refresh каждые 30 сек
```

### 2. Services (🖥️ ServicesView)
```swift
// Что показывает:
- Список всех сервисов:
  ✅ Telegram Bot (Running, 2h 15m)
  ✅ Marzban Monitor (Running, 2h 14m)
  ✅ Redis (Running, 2h 16m)
  ✅ PostgreSQL (Running, 2h 17m)

// Для каждого:
- Status indicator (зеленый/красный/желтый круг)
- Uptime
- Restart count
- CPU usage (%)
- Memory usage (MB)

// Действия:
- Start / Stop / Restart
- Click на сервис → Context menu
```

### 3. Users (👥 UsersView)
```swift
// Статистика:
- Total: 1234
- Active: 567
- Trial: 123
- New Today: 45

// Будущий функционал:
- Список пользователей
- Поиск по TG ID/username
- Редактирование баланса
- Управление подписками
```

### 4. Marzban (🌐 MarzbanView)
```swift
// Для каждого инстанса:
- Health status (Healthy/Degraded/Unhealthy)
- Active/Inactive
- Nodes count
- Users count
- Traffic (GB)

// Click → Детальная информация:
- Instance ID, Name, URL
- Priority
- Подробная статистика
- Upload/Download traffic
```

### 5. Broadcast (📢 BroadcastView)
```swift
// Функции:
- Текстовое поле для сообщения
- Выбор аудитории:
  - All Users
  - Users with Notifications Enabled
- Preview сообщения
- Подтверждение перед отправкой

// TODO: Интеграция с API
```

### 6. Logs (📋 LogsView)
```swift
// Функции:
- Переключение stdout/stderr
- Real-time streaming
- Поиск/фильтрация
- Auto-scroll
- Clear logs
- Monospaced шрифт
- Text selection для копирования
```

### 7. Settings (⚙️ SettingsView)
```swift
// Настройки:
- Backend URL (default: localhost:8080)
- Auto-start backend toggle
- Start/Stop/Restart backend
- App version & build
- Reset to defaults (danger zone)
```

---

## 🔧 Технологии

### Swift/SwiftUI
- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI (декларативный UI)
- **Deployment Target**: macOS 13.0+
- **Architecture**: MVVM pattern

### Async/Await
```swift
// Все API запросы асинхронные:
Task {
    let stats = try await apiService.fetchUserStats()
    // Update UI on main thread
}
```

### Process Management
```swift
// BackendManager запускает Python как subprocess:
let process = Process()
process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
process.arguments = ["python3", "-m", "uvicorn", ...]
```

### HTTP Client
```swift
// Современный URLSession + async/await:
func request<T: Decodable>(_ endpoint: String) async throws -> T {
    let (data, _) = try await session.data(for: request)
    return try JSONDecoder().decode(T.self, from: data)
}
```

---

## 🎨 UI/UX Особенности

### Элегантный дизайн
- **Native macOS**: Использует системные компоненты
- **Dark Mode**: Полная поддержка
- **SF Symbols**: Иконки из системной библиотеки
- **Sidebar Navigation**: Стандартный macOS pattern

### Анимации
- Smooth transitions между экранами
- Loading indicators
- Pull-to-refresh (где применимо)

### Responsive
- Адаптивный layout
- Минимальный размер: 1200x800
- Resizable окно

---

## 🚀 Запуск

### Метод 1: Xcode (рекомендуется)
```bash
1. Открыть Xcode
2. File → Open → mac/OrbitVPNManager/
3. ⌘ + R
```

### Метод 2: Создать проект с нуля
См. `QUICKSTART.md` для детальных инструкций.

---

## 📊 API Endpoints (уже работают)

Backend на FastAPI предоставляет:

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/status` | GET | System status |
| `/api/services` | GET | Список сервисов |
| `/api/services/{name}/start` | POST | Запустить сервис |
| `/api/services/{name}/stop` | POST | Остановить сервис |
| `/api/services/{name}/restart` | POST | Перезапустить |
| `/api/users/stats` | GET | Статистика пользователей |
| `/api/marzban/instances` | GET | Marzban инстансы |
| `/api/marzban/instances/{id}` | GET | Детали инстанса |
| `/api/metrics/history` | GET | История метрик |

---

## 🔮 Будущие улучшения

### Phase 2: User Management
- [ ] Полный список пользователей (таблица)
- [ ] Поиск/фильтрация
- [ ] Редактирование баланса
- [ ] Управление подписками
- [ ] История транзакций

### Phase 3: Analytics
- [ ] Графики доходов
- [ ] Retention metrics
- [ ] Conversion funnel
- [ ] Payment success rate

### Phase 4: Advanced Features
- [ ] Push notifications (macOS Notifications)
- [ ] Keyboard shortcuts
- [ ] Multiple windows support
- [ ] Export data (CSV, JSON)
- [ ] Scheduled broadcasts

### Phase 5: Distribution
- [ ] Code signing
- [ ] Notarization для macOS
- [ ] Auto-updates (Sparkle framework)
- [ ] App Store distribution

---

## 🤝 Интеграция с основным проектом

```
orbitvpn/
├── app/                  # Telegram bot (как есть)
├── manager/              # Backend manager (источник)
└── mac/
    ├── backend/          # Копия manager/ (автономная)
    └── OrbitVPNManager/  # Swift app
```

**Важно**: `mac/backend/` - это копия `manager/`. При обновлении `manager/`, нужно обновить `mac/backend/`:

```bash
# Синхронизация:
rsync -av --delete manager/ mac/backend/
```

---

## 📝 Лицензия

Proprietary - OrbitVPN Project

---

## 👨‍💻 Разработка

### Добавить новый экран:

1. Создать файл в `Views/MyNewView.swift`
2. Добавить в `ContentView.swift`:
```swift
NavigationLink(tag: 8, selection: $selectedTab) {
    MyNewView()
} label: {
    Label("My Feature", systemImage: "star.fill")
}
```

### Добавить новый API метод:

1. В `APIService.swift`:
```swift
func fetchMyData() async throws -> MyDataType {
    return try await request("/api/my-endpoint")
}
```

2. В View:
```swift
Task {
    let data = try await apiService.fetchMyData()
}
```

---

**Готово!** 🎉 У вас есть полноценный macOS менеджер для OrbitVPN!
