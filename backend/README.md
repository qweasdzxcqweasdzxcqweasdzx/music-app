# 🔧 Backend - Telegram Music Mini App

Бэкенд для музыкального стримингового сервиса в Telegram.

## 📋 Технологии

- **FastAPI** - современный Python веб-фреймворк
- **MongoDB** - база данных
- **Redis** - кэширование
- **JWT** - аутентификация
- **yt-dlp** - загрузка аудио с YouTube
- **FFmpeg** - обработка аудио

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env
nano .env  # или любой другой редактор
```

**Обязательные переменные:**
- `SECRET_KEY` - секретный ключ для JWT
- `TELEGRAM_BOT_TOKEN` - токен от BotFather

### 3. Запуск MongoDB и Redis

**Docker (рекомендуется):**
```bash
docker-compose up -d mongo redis
```

**Или локально:**
- MongoDB: https://www.mongodb.com/try/download/community
- Redis: https://redis.io/download

### 4. Запуск сервера

```bash
# Development
python main.py

# Или через uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Проверка

Откройте в браузере:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 📁 Структура проекта

```
backend/
├── main.py              # Точка входа FastAPI
├── config.py            # Конфигурация
├── database.py          # Подключение к БД
├── models.py            # Pydantic модели
├── auth.py              # Аутентификация
├── routes.py            # API роуты
├── services/
│   └── music_service.py # Музыкальный сервис
├── static/              # Статические файлы
├── .env                 # Переменные окружения
├── .env.example         # Пример переменных
├── requirements.txt     # Python зависимости
├── docker-compose.yml   # Docker конфигурация
└── Dockerfile           # Docker образ
```

## 🔑 API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/telegram` | Вход через Telegram |
| GET | `/api/me` | Данные пользователя |

### Музыка

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/search?q=...` | Поиск треков |
| GET | `/api/tracks/{id}` | Получить трек |
| GET | `/api/artists/{id}` | Получить артиста |
| GET | `/api/artists/{id}/tracks` | Треки артиста |

### Плейлисты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/playlists` | Создать плейлист |
| GET | `/api/playlists` | Мои плейлисты |
| GET | `/api/playlists/{id}` | Плейлист по ID |
| PUT | `/api/playlists/{id}` | Обновить плейлист |
| DELETE | `/api/playlists/{id}` | Удалить плейлист |
| POST | `/api/playlists/{id}/tracks` | Добавить трек |
| DELETE | `/api/playlists/{id}/tracks/{id}` | Удалить трек |

### История и лайки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/history` | История прослушиваний |
| POST | `/api/history` | Добавить в историю |
| GET | `/api/likes` | Любимые треки |
| POST | `/api/likes/{id}` | Лайкнуть трек |
| DELETE | `/api/likes/{id}` | Удалить лайк |

## 🔐 Аутентификация

### 1. Telegram WebApp

Фронтенд отправляет `init_data` от Telegram:

```javascript
import WebApp from '@twa-dev/sdk';

const initData = WebApp.initData;

const response = await fetch('/api/auth/telegram', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `init_data=${encodeURIComponent(initData)}`
});

const { access_token } = await response.json();
```

### 2. Использование токена

```javascript
const response = await fetch('/api/search?q=queen', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

## 🎵 Музыкальный сервис

### Источники музыки

1. **VK Music** (основной)
   - Неофициальный API
   - Требуется авторизация VK
   
2. **YouTube** (резервный)
   - Через yt-dlp
   - Для поиска оригинальных версий

3. **Собственная библиотека**
   - Загруженные треки
   - Лицензионный контент

### Проверка на цензуру

```python
from services.music_service import music_service

track = await music_service.get_track(track_id)
is_censored = await music_service.check_censorship(track)

if is_censored:
    original = await music_service.get_original_version(track)
    if original:
        track = original  # Используем оригинал
```

## 🗄️ База данных

### Коллекции MongoDB

**users:**
```json
{
  "_id": ObjectId,
  "telegram_id": "123456789",
  "username": "username",
  "first_name": "First",
  "last_name": "Last",
  "is_premium": false,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**tracks:**
```json
{
  "_id": ObjectId,
  "title": "Song Title",
  "artist": "Artist Name",
  "duration": 180,
  "stream_url": "https://...",
  "cover": "https://...",
  "source": "vk",
  "is_explicit": false,
  "play_count": 1000
}
```

**playlists:**
```json
{
  "_id": ObjectId,
  "user_id": "123456789",
  "name": "My Playlist",
  "description": "...",
  "tracks": ["track_id_1", "track_id_2"],
  "is_public": false
}
```

**play_history:**
```json
{
  "_id": ObjectId,
  "user_id": "123456789",
  "track_id": "track_id",
  "played_at": ISODate,
  "play_duration": 120
}
```

**likes:**
```json
{
  "_id": ObjectId,
  "user_id": "123456789",
  "track_id": "track_id",
  "created_at": ISODate
}
```

## 🐘 Docker

### Запуск всего стека

```bash
docker-compose up -d
```

Доступно:
- API: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379

### Сборка образа

```bash
docker build -t music-app-backend .
```

### Production

Для продакшена используйте nginx:

```bash
docker-compose -f docker-compose.yml up -d
```

## 📝 Интеграция с фронтендом

### 1. Настройка CORS

В `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Укажите ваш домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Деплой фронтенда

```bash
# В фронтенде
npm run build

# Копирование в backend
cp -r dist/* backend/static/
```

### 3. Переменные окружения

Обновите `.env` фронтенда:
```
VITE_API_URL=http://localhost:8000/api
```

## ⚠️ Важно

### Юридические аспекты

1. **VK Music API** - неофициальный, риск блокировки
2. **YouTube** - нарушение ToS для коммерческого использования
3. **Авторские права** - убедитесь в легальности контента

### Рекомендации

- Используйте для личного/тестового проекта
- Для продакшена рассмотрите:
  - Spotify API (официально)
  - Apple Music API
  - SoundCloud API
  - Собственную библиотеку

## 🔧 Troubleshooting

### MongoDB не подключается

```bash
# Проверьте URL подключения
echo $MONGODB_URL

# Проверьте статус MongoDB
docker ps | grep mongo
```

### Ошибка CORS

Добавьте ваш домен в `allow_origins` в `main.py`.

### JWT токен не работает

Проверьте `SECRET_KEY` в `.env` (одинаковый для бэкенда и фронтенда).

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
