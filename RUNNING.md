# 🚀 Ultimate Music App - Руководство по запуску

## Быстрый старт

### 1. Предварительные требования

**Обязательно:**
- Python 3.9+
- Node.js 18+
- Docker и Docker Compose (рекомендуется)

**Опционально:**
- Navidrome сервер (для личной коллекции)
- API ключи для AI сервисов

### 2. Установка и настройка

#### Вариант A: Docker (рекомендуется)

```bash
# Перейдите в директорию backend
cd music-app/backend

# Скопируйте конфигурацию
cp .env.example .env

# Отредактируйте .env - укажите обязательные поля:
# - SECRET_KEY (сгенерируйте: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET
# - TELEGRAM_BOT_TOKEN (опционально)

# Запустите Docker контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f backend
```

**Доступные сервисы:**
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (мониторинг): http://localhost:5555

#### Вариант B: Локальная установка

```bash
cd music-app/backend

# Установка зависимостей
pip install -r requirements.txt

# Запуск MongoDB и Redis (через Docker)
docker run -d -p 27017:27017 --name music_mongo mongo:7
docker run -d -p 6379:6379 --name music_redis redis:7-alpine

# Или установите локально

# Запуск сервера
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Запуск Celery worker (в отдельном терминале)
celery -A celery_worker.celery_app worker --loglevel=info

# Запуск Celery beat (в отдельном терминале)
celery -A celery_worker.celery_app beat --loglevel=info
```

### 3. Запуск фронтенда

```bash
cd music-app/frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка для продакшена
npm run build
```

Откройте: http://localhost:5173

---

## Получение API ключей

### Spotify API

1. Перейдите на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Войдите через Spotify аккаунт
3. Нажмите "Create App"
4. Заполните:
   - App name: `Ultimate Music App`
   - App description: `Music streaming platform`
   - Redirect URI: `http://localhost:8000/callback/spotify`
5. Скопируйте **Client ID** и **Client Secret**

### SoundCloud API

1. Перейдите на [SoundCloud Developers](https://soundcloud.com/you/apps)
2. Зарегистрируйте новое приложение
3. Укажите Redirect URI: `http://localhost:8000/callback/soundcloud`
4. Скопируйте **Client ID** и **Client Secret**

### Navidrome (личная коллекция)

1. Установите Navidrome: https://www.navidrome.org/docs/installation/
2. Запустите сервер (по умолчанию порт 4533)
3. Создайте пользователя
4. Укажите в `.env`:
   ```env
   NAVIDROME_URL=http://localhost:4533
   NAVIDROME_USERNAME=your_username
   NAVIDROME_PASSWORD=your_password
   ```

### AI Сервисы (опционально)

#### Suno AI
- Посетите https://suno.com
- Получите API ключ в настройках аккаунта

#### Mubert
- Зарегистрируйтесь на https://mubert.com
- Получите токен в API разделе

#### LALAL.AI
- Посетите https://www.lalal.ai/api/
- Купите кредиты и получите API ключ

#### ElevenLabs
- Зарегистрируйтесь на https://elevenlabs.io
- Получите API ключ в Profile Settings

#### Hugging Face
- Посетите https://huggingface.co/settings/tokens
- Создайте новый токен

---

## Проверка работы

### 1. Проверка здоровья

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "redis": "connected",
  "sources": {...},
  "telegram_bot": "disabled"
}
```

### 2. Проверка источников

```bash
curl http://localhost:8000/api/sources
```

### 3. Поиск музыки

```bash
curl "http://localhost:8000/api/search?q=weeknd&limit=5"
```

### 4. Единый поиск по всем источникам

```bash
curl "http://localhost:8000/api/search/unified?q=weeknd&limit=10&sources=spotify,soundcloud"
```

---

## Настройка подключения источников

### Подключение Navidrome

1. Убедитесь, что Navidrome сервер доступен
2. Добавьте в `.env`:
   ```env
   NAVIDROME_URL=http://your-navidrome:4533
   NAVIDROME_USERNAME=your_username
   NAVIDROME_PASSWORD=your_password
   ```
3. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```

### Подключение SoundCloud

1. Добавьте в `.env`:
   ```env
   SOUNDCLOUD_CLIENT_ID=your_client_id
   SOUNDCLOUD_CLIENT_SECRET=your_client_secret
   ```
2. Перезапустите backend

### Включение AI генерации

1. Добавьте нужные ключи в `.env`:
   ```env
   SUNO_API_KEY=...
   MUBERT_TOKEN=...
   LALAL_API_KEY=...
   ```
2. Убедитесь, что Celery worker запущен:
   ```bash
   docker-compose ps celery_worker
   ```

---

## Решение проблем

### Backend не запускается

```bash
# Проверьте логи
docker-compose logs backend

# Проверьте подключение к MongoDB
docker-compose logs mongo

# Перезапустите сервисы
docker-compose restart backend mongo redis
```

### Ошибка аутентификации Spotify

1. Проверьте Client ID и Secret в `.env`
2. Убедитесь, что Redirect URI совпадает с настройками в Spotify Dashboard
3. Перезапустите backend

### Celery worker не работает

```bash
# Проверьте логи
docker-compose logs celery_worker

# Убедитесь, что Redis доступен
docker-compose logs redis

# Перезапустите worker
docker-compose restart celery_worker
```

### AI генерация не работает

1. Проверьте API ключи в `.env`
2. Убедитесь, что Celery worker запущен
3. Проверьте логи worker:
   ```bash
   docker-compose logs -f celery_worker
   ```

### Фронтенд не подключается к backend

1. Создайте `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```
2. Перезапустите dev сервер:
   ```bash
   npm run dev
   ```

---

## Мониторинг

### Flower (Celery мониторинг)

Откройте http://localhost:5555

- Просмотр задач
- Статистика workers
- История выполнения

### Логи

```bash
# Все логи
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только Celery
docker-compose logs -f celery_worker
```

### MongoDB

```bash
# Подключение к MongoDB
docker exec -it music_mongo mongosh -u admin -p admin123

# Проверка коллекции
use ultimate_music_app
db.users.find().limit(5)
```

### Redis

```bash
# Подключение к Redis
docker exec -it music_redis redis-cli

# Проверка ключей
KEYS *

# Статистика
INFO
```

---

## Продакшен настройка

### 1. Безопасность

```env
# Смените SECRET_KEY
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Отключите DEBUG
DEBUG=False

# Настройте CORS
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. HTTPS через Nginx

1. Получите SSL сертификат (Let's Encrypt)
2. Положите файлы в `./ssl/`:
   - `cert.pem`
   - `privkey.pem`
3. Обновите `nginx.conf`
4. Перезапустите Nginx:
   ```bash
   docker-compose restart nginx
   ```

### 3. Внешний MongoDB

Используйте MongoDB Atlas или другой managed сервис:

```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ultimate_music_app
```

### 4. Backup

```bash
# Backup MongoDB
docker exec music_mongo mongodump --out=/backup

# Копирование backup
docker cp music_mongo:/backup ./mongodb-backup
```

---

## Команды Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f

# Масштабирование workers
docker-compose up -d --scale celery_worker=3

# Полная очистка
docker-compose down -v  # Удалит все данные!
```

---

## Тестирование API

### Через Swagger UI

Откройте http://localhost:8000/docs

### Через curl

```bash
# Поиск
curl "http://localhost:8000/api/search?q=weeknd&limit=5"

# Трек по ID
curl "http://localhost:8000/api/tracks/spotify:track:123456"

# Рекомендации
curl "http://localhost:8000/api/recommendations?seed_genres=pop&limit=10"

# AI генерация
curl -X POST "http://localhost:8000/api/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{"provider":"suno","prompt":"happy pop song"}'
```

---

## Поддержка

- GitHub Issues: [сообщить о проблеме]
- Документация: `/docs`
- API Docs: http://localhost:8000/docs
