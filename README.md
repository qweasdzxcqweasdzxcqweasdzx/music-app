# 🎵 Ultimate Music App

**Музыкальная платформа с Anti-Censorship системой**

![Version](https://img.shields.io/badge/version-3.1.0-blue)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)

---

## 📋 ОГЛАВЛЕНИЕ

1. [Быстрый старт](#быстрый-старт)
2. [Архитектура](#архитектура)
3. [Запуск проекта](#запуск-проекта)
4. [API Endpoints](#api-endpoints)
5. [Настройка](#настройка)
6. [Перенос на другой ПК](#перенос-на-другой-пк)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 БЫСТРЫЙ СТАРТ

### Автоматический запуск (все сервисы)

```bash
cd /home/c1ten12/music-app
./start-with-url-update.sh
```

### Ручной запуск (4 терминала)

**Терминал 1 — Backend (порт 8000):**
```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

**Терминал 2 — CORS Proxy (порт 8081):**
```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python cors_proxy_8081.py
```

**Терминал 3 — Cloudflare Tunnel (HTTPS):**
```bash
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081
```

**Терминал 4 — Frontend (разработка):**
```bash
cd /home/c1ten12/music-app/frontend
npm run dev
```

### Проверка работы

```bash
# Backend health
curl http://localhost:8000/health

# CORS Proxy test
curl http://localhost:8081/api/censorship/test

# Поиск треков
curl "http://localhost:8000/api/search?q=eminem&limit=5"
```

---

## 🏗️ АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Pages (Frontend)                    │
│  React 19 + Vite                                        │
│  https://qweasdzxcqweasdzxcqweasdzx.github.io/         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Cloudflare Tunnel (HTTPS)                     │
│  https://xxxx.trycloudflare.com                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           CORS Proxy (порт 8081)                        │
│  Python Flask - обход CORS                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Backend API (порт 8000)                       │
│  FastAPI + Python                                       │
│  ├─ MongoDB (данные пользователей, плейлисты)          │
│  ├─ Redis (кэширование)                                 │
│  ├─ Anti-Censorship System                              │
│  └─ Multi-source Music Integration                      │
└─────────────────────────────────────────────────────────┘
```

### Источники музыки

| Источник | Статус | Метод |
|----------|--------|-------|
| **SoundCloud** | ✅ | HTML scraping API |
| **YouTube** | ✅ | yt-dlp |
| **VK Music** | ⚠️ | API (резерв) |
| **Navidrome** | ⚠️ | Subsonic API |

---

## 🔥 ВОЗМОЖНОСТИ

### Anti-Censorship System
- **Распознавание** цензурных версий (clean, radio edit)
- **Fuzzy Matching** для поиска оригиналов
- **Мульти-платформенный поиск** (YouTube, SoundCloud, VK)
- **6 API endpoints** для работы с цензурой

### AI Сервисы
- **Suno AI** - генерация песен
- **Mubert** - фоновая музыка
- **ElevenLabs** - синтез речи
- **LALAL.AI** - разделение на стемы

### Персонализация
- Daily Mixes (ежедневные миксы)
- Release Radar (новые релизы)
- Discover Weekly (еженедельные рекомендации)
- История прослушиваний
- Любимые треки

---

## 📡 API ENDPOINTS

### Аутентификация
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/auth/telegram` | POST | Вход через Telegram |
| `/api/me` | GET | Данные пользователя |

### Поиск
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/search` | GET | Поиск по всем источникам |
| `/api/search/unified` | GET | Единый поиск |

### Anti-Censorship
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/censorship/check` | GET | Проверка на цензуру |
| `/api/censorship/find-original` | POST | Поиск оригинала |
| `/api/censorship/search-uncensored` | GET | Поиск explicit |
| `/api/censorship/analyze-batch` | POST | Массовый анализ |
| `/api/censorship/statistics` | GET | Статистика |
| `/api/censorship/replace-censored` | POST | Замена в плейлистах |

### Контент
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/tracks/{id}` | GET | Трек по ID |
| `/api/tracks/{id}/stream` | GET | URL потока |
| `/api/artists/{id}` | GET | Артист |
| `/api/albums/{id}` | GET | Альбом |
| `/api/genres` | GET | Жанры |
| `/api/top` | GET | Чарты |
| `/api/new` | GET | Новые релизы |

### Персонализация
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/recommendations` | GET | Рекомендации |
| `/api/daily-mixes` | GET | Ежедневные миксы |
| `/api/release-radar` | GET | Новые релизы |
| `/api/discover-weekly` | GET | Еженедельные открытия |

### Плейлисты
| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/playlists` | POST | Создание |
| `/api/playlists` | GET | Список |
| `/api/playlists/{id}/tracks` | POST | Добавить трек |

### Примеры запросов

```bash
# Health check
curl http://localhost:8000/health

# Поиск треков
curl "http://localhost:8000/api/search?q=eminem&limit=5"

# Проверка на цензуру
curl "http://localhost:8000/api/censorship/check?track_id=123"

# Swagger UI
# Откройте http://localhost:8000/docs
```

---

## 🔧 НАСТРОЙКА

### Backend (.env)

**Файл:** `backend/.env`

```env
# Приложение
APP_NAME=Ultimate Music App
DEBUG=True
HOST=0.0.0.0
PORT=8000

# База данных
MONGODB_URL=mongodb://localhost:27017
DB_NAME=ultimate_music_app
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=ваш-секретный-ключ-32-символа
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_токен

# SoundCloud
SOUNDCLOUD_CLIENT_ID=ваш_client_id
SOUNDCLOUD_CLIENT_SECRET=ваш_client_secret

# VK API
VK_CLIENT_ID=ваш_client_id

# Прокси (если нужен)
PROXY_URL=http://127.0.0.1:8888

# Анти-цензура
PREFER_ORIGINAL=True
AUTO_REPLACE_CENSORED=True
```

### Frontend (.env)

**Файл:** `frontend/.env`

```env
VITE_API_URL=http://localhost:8081/api
# Для production:
# VITE_API_URL=https://your-domain.com/api
```

### Зависимости

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## 📦 ПЕРЕНОС НА ДРУГОЙ ПК

### На старом ПК

```bash
cd /home/c1ten12/music-app

# 1. Закоммитьте изменения
git add . && git commit -m "Before migration" && git push origin main

# 2. Запустите скрипт бэкапа
./prepare-migration.sh
```

**Будет сохранено:**
- `.env` файлы (backend + frontend)
- База данных MongoDB (опционально)
- Музыкальная библиотека (опционально)

### На новом ПК

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git
cd music-app

# 2. Скопируйте migration_backup
cp -r /путь/к/migration_backup ./

# 3. Запустите настройку
./setup-on-new-pc.sh
```

**Требования к новому ПК:**
- Python 3.9+
- Node.js 18+
- MongoDB 6.0+
- Redis 6.0+ (опционально)
- RAM 4GB+
- Диск 10GB+

---

## 🛠️ TROUBLESHOOTING

### Сервер не запускается

```bash
# Проверка логов
tail -f /tmp/server.log

# Проверка портов
ss -tlnp | grep 8000

# Убить старые процессы
pkill -f uvicorn
pkill -f cors_proxy
```

### CORS ошибки в браузере

```bash
# Проверьте что CORS proxy работает
curl http://localhost:8081/api/censorship/test

# Если не работает - перезапустите
pkill -f cors_proxy
cd backend
source venv/bin/activate
python cors_proxy_8081.py &
```

### Cloudflare отключается

```bash
# Перезапуск
pkill -f cloudflared
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 &

# Или используйте скрипт
./start-cloudflare.sh
```

### MongoDB не подключается

```bash
# Проверка статуса
sudo systemctl status mongod

# Запуск
sudo systemctl start mongod

# Проверка
mongosh --eval "db.adminCommand('ping')"
```

### Ошибка импортов Python

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## 📁 СТРУКТУРА ПРОЕКТА

```
music-app/
├── backend/
│   ├── main.py, main_lite.py      # FastAPI приложение
│   ├── routes.py                  # API endpoints (~50+)
│   ├── cors_proxy_8081.py         # CORS proxy
│   ├── config.py                  # Конфигурация
│   ├── database.py                # MongoDB
│   ├── services/                  # Сервисы
│   │   ├── blues_detection_service.py  # Anti-Censorship
│   │   ├── youtube_service.py     # YouTube
│   │   ├── soundcloud_service.py  # SoundCloud
│   │   ├── audio_streaming_service.py
│   │   ├── recommendation_service.py
│   │   └── ...
│   ├── models/                    # Pydantic модели
│   ├── venv/                      # Python venv
│   └── requirements.txt           # Зависимости
│
├── frontend/
│   ├── src/
│   │   ├── api/musicApi.js        # API клиент
│   │   ├── components/            # React компоненты
│   │   └── pages/                 # Страницы
│   ├── dist/                      # Production build
│   ├── package.json
│   └── vite.config.js
│
├── start-with-url-update.sh       # Автозапуск
├── prepare-migration.sh           # Бэкап для переноса
├── setup-on-new-pc.sh             # Настройка на новом ПК
└── README.md                      # Этот файл
```

---

## 📊 СТАТУС КОМПОНЕНТОВ

| Компонент | Порт | Статус |
|-----------|------|--------|
| Backend API | 8000 | ✅ |
| CORS Proxy | 8081 | ✅ |
| Cloudflare Tunnel | - | ✅ |
| Frontend (GitHub) | - | ✅ |

**URL:**
- GitHub Pages: https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
- Swagger UI: http://localhost:8000/docs

---

## 🔗 ССЫЛКИ

- **GitHub:** https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app
- **Frontend:** https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
- **Backend API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs

---

**🎵 ПРИЯТНОГО ПРОСЛУШИВАНИЯ!**
