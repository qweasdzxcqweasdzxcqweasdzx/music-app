# 🎵 Ultimate Music App v3.0

> Музыкальная платформа «швейцарский нож» с интеграцией множественных источников и AI генерацией

[![Version](https://img.shields.io/badge/version-3.0.0-blue)]()
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)]()

---

## ⚡ Быстрый старт

### 1. Установка и запуск (Docker)

```bash
# Перейдите в директорию backend
cd music-app/backend

# Настройте окружение
cp .env.example .env
nano .env  # Укажите SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET

# Запустите все сервисы
docker-compose up -d

# Проверьте статус
docker-compose ps

# Логи
docker-compose logs -f backend
```

**Готово!** Откройте:
- **API Docs**: http://localhost:8000/docs
- **Backend**: http://localhost:8000

### 2. Фронтенд

```bash
cd music-app/frontend
npm install
npm run dev
```

Откройте: http://localhost:5173

---

## 🔑 Минимальная конфигурация

В `.env` укажите:

```env
# Обязательно
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Опционально
TELEGRAM_BOT_TOKEN=your_bot_token
```

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [README.md](README.md) | Полная документация |
| [RUNNING.md](RUNNING.md) | Руководство по запуску |
| [API_REFERENCE.md](API_REFERENCE.md) | Справочник API |
| [CHANGELOG_ULTIMATE.md](CHANGELOG_ULTIMATE.md) | История изменений |

---

## 🎯 Основные возможности

### 📻 Мульти-источники
- **Spotify** — миллионы треков
- **SoundCloud** — независимые артисты
- **Navidrome** — личная коллекция

### 🤖 AI Студия
- **Suno AI** — генерация песен
- **Mubert** — фоновая музыка
- **LALAL.AI** — разделение на стемы
- **ElevenLabs** — синтез голоса

### 🎚️ Умный миксер
- Smart Mix — персональные миксы
- Infinite Radio — бесконечное радио
- Mood Mix — по настроению

---

## 🔌 API Примеры

### Поиск музыки
```bash
curl "http://localhost:8000/api/search?q=weeknd&limit=5"
```

### Умный микс
```bash
curl "http://localhost:8000/api/mixer/smart?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### AI генерация
```bash
curl -X POST "http://localhost:8000/api/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{"provider":"suno","prompt":"happy pop song"}'
```

---

## 🐘 Docker сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| backend | 8000 | FastAPI сервер |
| mongo | 27017 | База данных |
| redis | 6379 | Кэш и очереди |
| celery_worker | - | AI задачи |
| flower | 5555 | Мониторинг |

---

## 🛠️ Технологии

**Backend:** FastAPI, MongoDB, Redis, Celery  
**Frontend:** React 19, Vite  
**AI:** Suno, Mubert, LALAL.AI, ElevenLabs, Hugging Face

---

## 📝 Лицензия

MIT License

---

**v3.0** — Multi-source + AI generation + Smart Mixer
