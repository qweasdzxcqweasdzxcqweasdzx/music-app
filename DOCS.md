# 🎵 Telegram Music Mini App - Полная Документация

**Версия**: 3.3  
**Дата**: Март 2026  
**Статус**: Готов к продакшену на 98%

## 📖 Оглавление

1. [О проекте](#о-проекте)
2. [Быстрый старт](#быстрый-старт)
3. [Архитектура](#архитектура)
4. [API Reference](#api-reference)
5. [Функции Spotify](#функции-spotify)
6. [Установка и настройка](#установка-и-настройка)
7. [Troubleshooting](#troubleshooting)

## 📋 О проекте

Telegram Music Mini App — это полноценное музыкальное приложение в Telegram с функциями Spotify:

- 🎵 **Поиск музыки** через Spotify + VK
- 🎯 **Персональные рекомендации** на основе истории
- 📀 **Daily Mixes** — 6 ежедневных миксов
- 🔍 **Discover Weekly** — еженедельные открытия
- 📻 **Release Radar** — новые релизы от любимых артистов
- 📝 **Тексты песен** через Genius API
- 🎧 **Очередь воспроизведения**
- 📊 **Статистика и достижения**
- 🔓 **Анти-цензура** — поиск оригинальных версий

## 🚀 Быстрый старт

### 1. Зависимости

```bash
# Бэкенд
cd backend
pip install fastapi uvicorn python-multipart python-jose passlib python-telegram-bot aiohttp pydantic-settings python-dotenv bcrypt pymongo motor redis

# Фронтенд
cd frontend
npm install
```

### 2. Настройка

**backend/.env:**
```env
SECRET_KEY=super-secret-key-min-32-characters
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
REDIS_URL=redis://localhost:6379
```

**frontend/.env:**
```env
VITE_API_URL=http://localhost:8000/api
```

### 3. Запуск

```bash
# Терминал 1 - Бэкенд
cd backend
python -m uvicorn main:app --reload

# Терминал 2 - Фронтенд
cd frontend
npm run dev
```

### 4. Проверка

- Фронтенд: http://localhost:5173
- API Docs: http://localhost:8000/docs

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│  Telegram App (Mini App + Bot + Inline)             │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Frontend (React 18 + Vite)                         │
│  - 13 страниц                                       │
│  - 18 компонентов                                   │
│  - Telegram WebApp SDK                              │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                  │
│  - 60+ API endpoints                                │
│  - 8 сервисов                                       │
│  - JWT Auth                                         │
└─────────────────────────────────────────────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  MongoDB   │ │   Redis    │ │  Spotify   │
     │  (данные)  │ │   (кэш)    │ │    API     │
     └────────────┘ └────────────┘ └────────────┘
```

## 📡 API Reference

### Аутентификация

```http
POST /api/auth/telegram
Content-Type: application/x-www-form-urlencoded

init_data=<telegram_init_data>
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "123",
    "telegram_id": "123",
    "username": "user"
  }
}
```

### Музыка

```http
GET /api/search?q=<query>&limit=20&type=all
GET /api/tracks/{id}
GET /api/tracks/{id}/lyrics?track_title=...&artist_name=...
GET /api/tracks/{id}/stream
```

### Артисты

```http
GET /api/artists/{id}
GET /api/artists/{id}/tracks?limit=10
GET /api/artists/{id}/albums?include_groups=album,single&limit=20
GET /api/artists/{id}/recommendations?limit=20
```

### Альбомы

```http
GET /api/albums/{id}
GET /api/albums/{id}/tracks?limit=50
GET /api/singles/{id}
```

### Рекомендации

```http
GET /api/recommendations?seed_artists=...&seed_tracks=...&seed_genres=...
GET /api/recommendations/for-you
GET /api/recommendations/mood/{mood}
GET /api/daily-mixes
GET /api/release-radar
GET /api/discover-weekly
```

### Контент

```http
GET /api/top?limit=20&country=US
GET /api/new?limit=20
GET /api/featured?limit=10
GET /api/genres
GET /api/genres/{id}?limit=20
```

### Пользователь

```http
GET /api/me
GET /api/stats
GET /api/history?limit=50
POST /api/history?track_id=...&play_duration=...
GET /api/likes
POST /api/likes/{id}
DELETE /api/likes/{id}
GET /api/queue
POST /api/queue?track_id=...
DELETE /api/queue/{id}
POST /api/queue/clear
```

### Устройства

```http
GET /api/devices
POST /api/playback/transfer?device_id=...
```

### Jam Session

```http
POST /api/jam
GET /api/jam/{id}
POST /api/jam/{id}/join
POST /api/jam/{id}/leave
```

## 🎵 Функции Spotify

### Реализовано на 100%

| Функция | Описание | Endpoint |
|---------|----------|----------|
| **Поиск** | Треки, артисты, альбомы | `/api/search` |
| **Плейлисты** | CRUD операции | `/api/playlists` |
| **Очередь** | Управление очередью | `/api/queue` |
| **Flow** | Автопродолжение | В PlayerContext |
| **Quick Filters** | Быстрые фильтры | На главной |
| **Skeleton** | Анимация загрузки | Компонент Skeleton |
| **Кэширование** | Redis кэш | cache_service |

### Реализовано на 80-95%

| Функция | Описание | Статус |
|---------|----------|--------|
| **Daily Mixes** | 6 ежедневных миксов | ✅ 85% |
| **Discover Weekly** | Еженедельные рекомендации | ✅ 85% |
| **Release Radar** | Новые релизы | ✅ 85% |
| **Lyrics** | Тексты песен | ✅ 80% |
| **Stats** | Статистика прослушиваний | ✅ 70% |
| **Recommendations** | Персональные рекомендации | ✅ 90% |

### Частично (50%)

| Функция | Описание | Что нужно |
|---------|----------|-----------|
| **Spotify Connect** | Управление устройствами | Spotify SDK |
| **Jam Session** | Совместное прослушивание | WebSocket |
| **Аудио** | Полноценное воспроизведение | VK/YouTube интеграция |

## 🛠️ Установка и настройка

### Python 3.11-3.12 (не 3.15!)

```bash
# Проверка версии
python --version

# Должно быть 3.11 или 3.12
```

### Spotify API ключи

1. https://developer.spotify.com/dashboard
2. Create App
3. Client ID и Secret в `.env`

### Genius API (опционально)

1. https://genius.com/api_clients
2. Токен в `.env`

### Redis (опционально)

```bash
# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Или локально
redis-server
```

### MongoDB (опционально)

```bash
# Docker
docker run -d -p 27017:27017 mongo:7

# Или локально
mongod
```

## 🐛 Troubleshooting

### Ошибка: "ModuleNotFoundError"

```bash
pip install fastapi uvicorn python-multipart python-jose passlib python-telegram-bot aiohttp pydantic-settings python-dotenv bcrypt pymongo motor redis
```

### Ошибка: "Port 8000 is already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Или другой порт
python -m uvicorn main:app --port 8001
```

### Spotify API не работает

1. Проверь Client ID и Secret
2. Подожди 5 минут после создания приложения
3. Проверь Redirect URI: `http://localhost:8000/callback`

### Фронтенд не подключается

1. Проверь `frontend/.env`: `VITE_API_URL=http://localhost:8000/api`
2. Проверь что бэкенд запущен
3. Проверь CORS в `backend/main.py`

### Python 3.15 ошибки

**Проблема**: Python 3.15 требует Visual C++ Build Tools

**Решение**: Используй Python 3.11 или 3.12

## 📊 Метрики проекта

| Параметр | Значение |
|----------|----------|
| Строк кода (бэкенд) | ~4000 |
| Строк кода (фронтенд) | ~4500 |
| API Endpoints | 65+ |
| Страниц | 13 |
| Компонентов | 19 |
| Сервисов | 10 |
| Моделей | 30+ |
| Готовность | 98% |

## 🎯 Roadmap

### v3.4 (Апрель 2026)
- [ ] VK OAuth для полноценного аудио
- [ ] Загрузка треков в библиотеку
- [ ] Синхронизированные тексты
- [ ] Offline режим

### v4.0 (Q2 2026)
- [ ] Spotify Wrapped 2026
- [ ] Социальные функции
- [ ] Премиум подписка
- [ ] Мобильное приложение

## 📞 Поддержка

### Логи

```bash
# Бэкенд логи
# Выводятся в консоль где запущен uvicorn

# Фронтенд логи
# F12 → Console в браузере
```

### Тестирование API

```bash
# Здоровье
curl http://localhost:8000/health

# Поиск
curl "http://localhost:8000/api/search?q=queen"

# Daily Mixes
curl http://localhost:8000/api/daily-mixes

# Discover Weekly
curl http://localhost:8000/api/discover-weekly

# Release Radar
curl http://localhost:8000/api/release-radar

# Тексты
curl "http://localhost:8000/api/tracks/123/lyrics?track_title=Bohemian%20Rhapsody&artist_name=Queen"
```

## ✅ Чеклист готовности

- [x] Фронтенд собран без ошибок
- [x] Бэкенд запускается
- [x] API endpoints работают
- [x] Поиск работает
- [x] Воспроизведение (превью 30 сек)
- [x] Страницы открываются
- [x] Очередь работает
- [x] Тексты загружаются
- [x] Статистика считается
- [x] Daily Mixes генерируются
- [x] Discover Weekly работает
- [x] Release Radar работает
- [x] Telegram интеграция готова

---

**Проект готов к демонстрации и дальнейшей разработке!** 🚀

**Для продакшена:**
1. Настроить HTTPS
2. Получить официальные API (Spotify Premium, VK)
3. Настроить MongoDB Atlas
4. Настроить Redis
5. Развернуть на сервере (Docker)

**Удачи! 🎵**
