# 🚀 Запуск Telegram Music Mini App на Windows

## Быстрый старт (5 минут)

### Шаг 1: Установка зависимостей

#### 1.1 Python (если нет)
1. Скачайте Python 3.11+ с https://www.python.org/downloads/
2. Установите, отметив галочку "Add Python to PATH"

#### 1.2 Node.js (если нет)
1. Скачайте с https://nodejs.org/
2. Установите LTS версию

#### 1.3 Docker Desktop (рекомендуется)
1. Скачайте с https://www.docker.com/products/docker-desktop/
2. Установите и запустите

### Шаг 2: Настройка бэкенда

```powershell
# Перейдите в директорию backend
cd backend

# Скопируйте .env.example в .env
copy .env.example .env

# Откройте .env в блокноте и заполните:
notepad .env
```

**Обязательные поля:**
```env
SECRET_KEY=super-secret-key-min-32-characters-change-this
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Получение токена Telegram:**
1. Откройте Telegram, найдите @BotFather
2. Отправьте `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте полученный токен в `.env`

### Шаг 3: Запуск через Docker (рекомендуется)

```powershell
# В директории backend
docker-compose up -d
```

Проверка:
```powershell
docker-compose ps
```

Должны работать:
- `music_backend` — API сервер
- `music_mongo` — база данных
- `music_redis` — кэш

Откройте в браузере:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Шаг 4: Запуск фронтенда

```powershell
# В новой консоли, перейдите в frontend
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

Откройте: http://localhost:5173

### Шаг 5: Настройка Telegram Mini App

1. Откройте @BotFather в Telegram
2. Отправьте `/newapp`
3. Выберите вашего бота
4. Укажите URL: `http://localhost:8000/static/index.html`
5. Придумайте короткое имя для кнопки

Теперь откройте вашего бота и нажмите кнопку "Menu" или отправьте `/start`

---

## Запуск без Docker

### Шаг 1: Установка MongoDB

1. Скачайте MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Установите с настройками по умолчанию
3. Запустите службу MongoDB

### Шаг 2: Установка Redis (опционально)

1. Скачайте Redis для Windows: https://github.com/microsoftarchive/redis/releases
2. Распакуйте и запустите `redis-server.exe`

Или используйте WSL:
```powershell
wsl
sudo apt update
sudo apt install redis-server
redis-server
```

### Шаг 3: Установка Python зависимостей

```powershell
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Шаг 4: Запуск бэкенда

```powershell
# Убедитесь что MongoDB запущен
# Обновите MONGODB_URL в .env если нужно:
# MONGODB_URL=mongodb://localhost:27017

python main.py
```

### Шаг 5: Запуск фронтенда

```powershell
cd frontend
npm install
npm run dev
```

---

## Проверка работы

### 1. Проверка API

Откройте http://localhost:8000/health

Должно вернуться:
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "telegram_bot": "running"
}
```

### 2. Проверка фронтенда

Откройте http://localhost:5173

Должна загрузиться главная страница с приветствием

### 3. Проверка бота

1. Откройте вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "🎵 Открыть плеер"

---

## Частые проблемы

### Ошибка: "ModuleNotFoundError: No module named 'xxx'"

```powershell
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Ошибка: "MongoServerError: Authentication failed"

Проверьте `.env`:
```env
MONGODB_URL=mongodb://admin:admin123@localhost:27017/music_app?authSource=admin
```

Или используйте без авторизации (для разработки):
```env
MONGODB_URL=mongodb://localhost:27017
```

### Ошибка: "ECONNREFUSED" при запуске фронтенда

Убедитесь что бэкенд запущен:
```powershell
docker-compose ps
# или
python main.py
```

### Бот не отвечает

1. Проверьте токен в `.env`
2. Перезапустите бэкенд
3. Проверьте логи:
   ```powershell
   docker-compose logs -f backend
   ```

### Фронтенд не подключается к API

1. Проверьте `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

2. Проверьте CORS в `backend/main.py` (должно быть `allow_origins=["*"]`)

---

## Деплой на сервер (production)

### 1. Подготовка сервера

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose python3-pip -y
```

### 2. Настройка домена

Получите SSL сертификат:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 3. Развёртывание

```bash
# Клонирование репозитория
git clone <your-repo>
cd музыкавтг/backend

# Настройка .env
cp .env.example .env
nano .env  # Заполните переменные

# Запуск
docker-compose up -d
```

### 4. Настройка Nginx

Отредактируйте `nginx.conf`:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Настройка Telegram для продакшена

В @BotFather укажите URL:
```
https://your-domain.com/static/index.html
```

---

## Полезные команды

### Docker

```powershell
# Просмотр логов
docker-compose logs -f backend

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
```

### MongoDB

```powershell
# Подключение к MongoDB
docker-compose exec mongo mongosh -u admin -p admin123

# Просмотр коллекций
use music_app
show collections
db.users.find().limit(5)
```

### Фронтенд

```powershell
# Сборка для продакшена
npm run build

# Предпросмотр сборки
npm run preview

# Линтинг
npm run lint
```

---

## Контакты и поддержка

- Telegram: @yourusername
- GitHub: Issues
- Документация: /backend/docs

**Удачи! 🎵**
