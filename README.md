# 🎵 Ultimate Music App v3.0

**Полноценная музыкальная платформа "швейцарский нож" с интеграцией множественных источников и AI генерацией**

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-19-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

---

## ✨ Ключевые возможности

### 🔌 Мульти-источники музыки

| Источник | Описание | Статус |
|----------|----------|--------|
| **SoundCloud** | Независимые артисты, ремиксы, основной источник | ✅ |
| **Navidrome** | Личная коллекция (Subsonic API) | ✅ |
| **VK Music** | Резервный источник | ⚠️ |
| **YouTube** | Поиск оригиналов, видео | ⚠️ |

### 🤖 AI Студия

| Сервис | Назначение | Статус |
|--------|------------|--------|
| **Suno AI** | Генерация песен по промпту | ✅ |
| **Mubert** | Фоновая музыка для задач | ✅ |
| **MusicGen** | Короткие аудио-клипы | ✅ |
| **LALAL.AI** | Разделение на стемы (вокал, бас, ударные) | ✅ |
| **ElevenLabs** | Синтез речи/вокала | ✅ |
| **Replicate** | Разные AI модели | ✅ |

### 🎯 Персонализация

- **Smart Mixer** — умное комбинирование треков из разных источников
- **Infinite Radio** — бесконечное радио на основе любого трека
- **Daily Mixes** — ежедневные персональные миксы
- **Release Radar** — новые релизы любимых артистов
- **Discover Weekly** — еженедельные открытия
- **Mood-based** — подборки по настроению

### 📱 Платформы

- **Telegram Mini App** — встроенное приложение в Telegram
- **Web** — полноценный веб-интерфейс
- **React Native** — iOS и Android (в разработке)

### 🔐 Безопасность

- **JWT аутентификация** — токены с шифрованием
- **OAuth 2.0** — безопасное подключение сторонних сервисов
- **Шифрование токенов** — Fernet (cryptography)
- **Rate Limiting** — защита от злоупотреблений

---

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
cd music-app/backend

# Копирование .env
cp .env.example .env
nano .env  # Заполните необходимые ключи
```

### 2. Заполнение .env

**Обязательные поля:**
```env
# SoundCloud (основной источник)
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret

# JWT (сгенерируйте случайную строку)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Telegram (для бота)
TELEGRAM_BOT_TOKEN=your_bot_token
```

**Опциональные (для расширенных функций):**
```env
# Navidrome (личная коллекция)
NAVIDROME_URL=http://localhost:4533
NAVIDROME_USERNAME=
NAVIDROME_PASSWORD=

# VK Music (резерв)
VK_CLIENT_ID=
VK_CLIENT_SECRET=

# AI сервисы
SUNO_API_KEY=
MUBERT_TOKEN=
LALAL_API_KEY=
ELEVENLABS_API_KEY=
HUGGINGFACE_TOKEN=
```

### 3. Запуск через Docker (рекомендуется)

```bash
cd backend
docker-compose up -d
```

**Сервисы:**
- `mongo` — база данных (порт 27017)
- `redis` — кэш и очереди (порт 6379)
- `backend` — FastAPI сервер (порт 8000)
- `celery_worker` — фоновые задачи AI
- `celery_beat` — периодические задачи
- `flower` — мониторинг Celery (порт 5555)
- `nginx` — reverse proxy (порты 80, 443)

### 4. Проверка

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower**: http://localhost:5555

### 5. Запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

Откройте: http://localhost:5173

---

## 📁 Структура проекта

```
music-app/
├── backend/
│   ├── services/
│   │   ├── music_source_base.py      # Базовый интерфейс источников
│   │   ├── soundcloud_source_adapter.py # SoundCloud адаптер
│   │   ├── navidrome_source_adapter.py   # Navidrome адаптер
│   │   ├── navidrome_service.py      # Navidrome/Subsonic API
│   │   ├── soundcloud_service.py     # SoundCloud API
│   │   ├── ai_music_service.py       # AI генерация (Suno, Mubert, etc.)
│   │   ├── smart_mixer_service.py    # Умный миксер
│   │   ├── websocket_manager.py      # WebSocket для реального времени
│   │   ├── secure_storage.py         # Безопасное хранение токенов
│   │   ├── recommendation_service.py # Рекомендации
│   │   ├── daily_mixes_service.py    # Daily Mixes
│   │   ├── discover_weekly_service.py # Discover Weekly
│   │   ├── release_radar_service.py  # Release Radar
│   │   ├── lyrics_service.py         # Тексты песен
│   │   ├── cache_service.py          # Redis кэш
│   │   └── audio_streaming_service.py # Аудио стриминг
│   ├── main.py                       # FastAPI приложение
│   ├── routes.py                     # API endpoints (50+)
│   ├── models.py                     # Pydantic модели
│   ├── celery_worker.py              # Фоновые задачи
│   ├── docker-compose.yml            # Docker конфигурация
│   └── .env.example                  # Шаблон конфигурации
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── musicApi.js           # API клиент
│   │   ├── components/
│   │   │   ├── Player.jsx            # Главный плеер
│   │   │   ├── MiniPlayer.jsx        # Мини-плеер
│   │   │   ├── TrackCard.jsx         # Карточка трека
│   │   │   ├── ArtistCard.jsx        # Карточка артиста
│   │   │   ├── AlbumCard.jsx         # Карточка альбома
│   │   │   ├── Sidebar.jsx           # Боковая панель
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Home.jsx              # Главная (рекомендации)
│   │   │   ├── Search.jsx            # Поиск
│   │   │   ├── Artist.jsx            # Страница артиста
│   │   │   ├── Album.jsx             # Страница альбома
│   │   │   ├── Library.jsx           # Библиотека
│   │   │   ├── DailyMixes.jsx        # Daily Mixes
│   │   │   ├── FullPlayer.jsx        # Полный плеер
│   │   │   └── ...
│   │   └── contexts/
│   │       └── PlayerContext.jsx     # Управление плеером
│   └── package.json
│
└── docs/
    ├── API.md                        # API документация
    ├── DEPLOY.md                     # Деплой
    └── AI_SETUP.md                   # Настройка AI сервисов
```

---

## 🔑 API Endpoints

### Источники музыки

```
GET    /api/sources                  # Список доступных источников
GET    /api/search/unified?q=...     # Единый поиск по всем источникам
```

### Аутентификация

```
POST   /api/auth/telegram            # Вход через Telegram
GET    /api/me                       # Данные пользователя
```

### Музыка

```
GET    /api/search?q=...             # Поиск
GET    /api/tracks/{id}              # Трек по ID
GET    /api/tracks/{id}/stream       # URL потока
```

### Артисты

```
GET    /api/artists/{id}             # Информация об артисте
GET    /api/artists/{id}/tracks      # Топ треки
GET    /api/artists/{id}/albums      # Альбомы и синглы
GET    /api/artists/{id}/recommendations # Похожие артисты
```

### Альбомы

```
GET    /api/albums/{id}              # Информация об альбоме
GET    /api/albums/{id}/tracks       # Треки альбома
```

### Рекомендации

```
GET    /api/recommendations          # На основе seed
GET    /api/recommendations/for-you  # Персональные
GET    /api/recommendations/mood/{mood} # По настроению
```

### Умный миксер

```
GET    /api/mixer/smart              # Умный микс
GET    /api/mixer/radio/{track_id}   # Бесконечное радио
GET    /api/mixer/mood/{mood}        # Микс по настроению
GET    /api/mixer/genre/{genre}      # Микс по жанру
```

### AI Генерация

```
POST   /api/ai/generate              # Генерация музыки
GET    /api/ai/status/{task_id}      # Статус генерации
POST   /api/ai/separate              # Разделение на стемы
POST   /api/ai/voice                 # Синтез голоса
```

### WebSocket

```
WS     /ws                           # WebSocket для реального времени
```

---

## 🎯 Как работает Умный Миксер

### Алгоритм

1. **Анализ предпочтений**
   - История прослушиваний (последние 100 треков)
   - Любимые треки (лайки)
   - Топ артистов

2. **Определение источников**
   - Navidrome — приоритет для личной коллекции
   - SoundCloud — основной источник для новинок и ремиксов
   - AI — для уникального контента

3. **Генерация микса**
   - Получение рекомендаций из каждого источника
   - Взвешенное перемешивание
   - Удаление дубликатов

4. **Взвешенный приоритет**
   ```
   Navidrome:  1.0 (highest)
   SoundCloud: 0.9
   AI:         0.3
   ```

---

## 🤖 AI Генерация

### Поддерживаемые сервисы

#### Suno AI
- Генерация полноценных песен с вокалом
- Длительность: до 2 минут
- Время генерации: ~30-60 секунд

```python
# Через API
POST /api/ai/generate
{
    "provider": "suno",
    "prompt": "A happy pop song about summer",
    "tags": "pop happy summer",
    "title": "Summer Vibes"
}
```

#### Mubert
- Фоновая музыка для работы/учебы
- Бесконечные потоки
- Настройка по настроению

#### LALAL.AI
- Разделение трека на стемы
- Доступные стемы: vocals, instrumental, drums, bass, guitar, piano

```python
POST /api/ai/separate
{
    "audio_url": "https://...",
    "stem_type": "vocals"
}
```

#### ElevenLabs
- Синтез речи и вокала
- 10+ предустановленных голосов
- Настройка стабильности и стиля

---

## 🐘 Docker

### Запуск всего стека

```bash
cd backend
docker-compose up -d
```

### Логи

```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f flower
```

### Остановка

```bash
docker-compose down
docker-compose down -v  # Удалить данные БД
```

### Масштабирование

```bash
# Увеличение количества workers
docker-compose up -d --scale celery_worker=3
```

---

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React/React Native)                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Player  │  Search  │  Library  │  AI Studio     │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ REST API + WebSocket
┌────────────────────▼────────────────────────────────────┐
│  Backend API Gateway (FastAPI)                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Source Manager (единый интерфейс)                │  │
│  └───────────────────────────────────────────────────┘  │
└───────┬──────────────────┬─────────────────────────────┘
        │                  │
┌───────▼──────┐  ┌────────▼────────┐
│  SoundCloud  │  │  Navidrome      │
│   Adapter    │  │   Adapter       │
└───────┬──────┘  └────────┬────────┘
        │                  │
┌───────▼──────┐  ┌────────▼────────┐
│ SoundCloud   │  │  Navidrome      │
│     API      │  │   Server        │
└──────────────┘  └─────────────────┘

        ┌──────────────────────────────────────────┐
        │         AI Services (Celery)             │
        │  ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
        │  │  Suno   │ │ Mubert  │ │ LALAL.AI    │ │
        │  │ MusicGen│ │ElevenLabs││ Replicate   │ │
        │  └─────────┘ └─────────┘ └─────────────┘ │
        └──────────────────────────────────────────┘
```

---

## ⚠️ Важные замечания

### Лицензии и авторские права

- **SoundCloud** — зависит от лицензии каждого трека
- **Navidrome** — ваша личная коллекция
- **AI генерация** — проверьте условия каждого сервиса

### Ограничения API

| Сервис | Лимит | Примечание |
|--------|-------|------------|
| SoundCloud | 10000 req/day | Зависит от приложения |
| Suno AI | 50 gen/day | Для бесплатного тарифа |
| LALAL.AI | Платно за трек | $1-5 за разделение |

### Рекомендации по продакшену

1. **Смените SECRET_KEY** на случайную строку 32+ символов
2. **Настройте HTTPS** через Nginx
3. **Используйте внешний MongoDB** (не в Docker)
4. **Настройте backup** для базы данных
5. **Мониторинг** через Flower + Prometheus

---

## 🛠️ Технологии

### Backend
- **FastAPI** — веб-фреймворк
- **MongoDB** + Motor — асинхронная БД
- **Redis** — кэш и очереди задач
- **Celery** — фоновые задачи
- **Cryptography** — шифрование токенов

### Frontend
- **React 19** + Vite
- **React Router DOM** — навигация
- **Telegram WebApp SDK** — интеграция

### AI/ML
- **Suno AI** — генерация песен
- **Mubert** — фоновая музыка
- **Hugging Face** — MusicGen
- **LALAL.AI** — разделение на стемы
- **ElevenLabs** — синтез речи

---

## 📝 Лицензия

MIT License

---

**v3.0** — Multi-source integration + AI generation + Smart Mixer

**Сделано с ❤️ для Ultimate Music Community**
