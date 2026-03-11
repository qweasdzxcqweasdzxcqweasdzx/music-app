# 🚀 Перенос Ultimate Music App на другой ПК

**Полное руководство по миграции проекта**

---

## 📋 ЧТО НУЖНО ПЕРЕНЕСТИ

| Компонент | Способ переноса | Примечание |
|-----------|----------------|------------|
| **Исходный код** | Git (GitHub) | ✅ Уже в репозитории |
| **База данных** | MongoDB dump/restore | Локальные данные |
| **Переменные окружения** | Вручную (.env файлы) | 🔒 Секретные данные |
| **Музыкальная библиотека** | Копирование папки | Опционально |
| **Зависимости** | Установка заново | pip + npm |

---

## 📦 ЭТАП 1: ПОДГОТОВКА НА ТЕКУЩЕМ ПК

### 1.1. Проверка репозитория

```bash
cd /home/c1ten12/music-app

# Проверка статуса Git
git status

# Если есть изменения - закоммитьте
git add .
git commit -m "Final commit before migration"
git push origin main
```

### 1.2. Сохранение .env файлов

```bash
# Создаём резервные копии .env файлов
cp /home/c1ten12/music-app/backend/.env /home/c1ten12/music-app/backend/.env.backup
cp /home/c1ten12/music-app/frontend/.env /home/c1ten12/music-app/frontend/.env.backup

# Просмотр содержимого (для копирования)
cat /home/c1ten12/music-app/backend/.env
```

### 1.3. Экспорт базы данных (опционально)

```bash
# Экспорт MongoDB
mongodump --uri="mongodb://localhost:27017" --db=ultimate_music_app --out=/home/c1ten12/music-app/backup/mongodb

# Экспорт Redis (если используется)
redis-cli SAVE
cp /var/lib/redis/dump.rdb /home/c1ten12/music-app/backup/redis/
```

### 1.4. Сохранение музыкальной библиотеки (опционально)

```bash
# Проверка размера библиотеки
du -sh /home/c1ten12/music-app/backend/music_library/

# Если нужно - создаём архив
tar -czvf music_library_backup.tar.gz /home/c1ten12/music-app/backend/music_library/
```

---

## 💻 ЭТАП 2: НАСТРОЙКА НА НОВОМ ПК

### 2.1. Требования к системе

**Минимальные требования:**
- **ОС:** Linux (Ubuntu 20.04+), macOS, Windows 10+ (WSL2)
- **Python:** 3.9 - 3.12
- **Node.js:** 18+ 
- **MongoDB:** 6.0+ (локально или Docker)
- **Redis:** 6.0+ (локально или Docker)
- **RAM:** 4GB+ (8GB рекомендуется)
- **Диск:** 10GB+ свободного места

### 2.2. Установка зависимостей ОС

#### Ubuntu/Debian:
```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Python и Node.js
sudo apt install -y python3.12 python3.12-venv python3-pip
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Установка MongoDB (официальный репозиторий)
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Установка Redis
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis

# Установка Git
sudo apt install -y git
```

#### macOS:
```bash
# Установка через Homebrew
brew install python@3.12 node mongodb redis git
brew services start mongodb-community
brew services start redis
```

#### Windows (WSL2):
```bash
# Установите WSL2 и Ubuntu 22.04 из Microsoft Store
# Затем следуйте инструкции для Ubuntu
```

---

## 📥 ЭТАП 3: КЛОНИРОВАНИЕ ПРОЕКТА

### 3.1. Клонирование репозитория

```bash
# Создание директории для проекта
mkdir -p ~/projects
cd ~/projects

# Клонирование репозитория
git clone https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app.git
cd music-app

# Проверка структуры
ls -la
```

### 3.2. Восстановление .env файлов

```bash
# Backend .env
cd backend
cp .env.example .env
nano .env  # Вставьте значения из старого .env

# Frontend .env
cd ../frontend
cp .env.example .env  # или создайте вручную
nano .env
```

**Пример backend/.env:**
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
SECRET_KEY=ваш-новый-секретный-ключ-32-символа
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Telegram Bot
TELEGRAM_BOT_TOKEN=8486711572:AAFpmQ_0vzjHRgi61FdnXLdRcbIaA7Pe8TA

# SoundCloud
SOUNDCLOUD_CLIENT_ID=gZX8jnL55gAHKRgcpIMt9nTUKo94Un61
SOUNDCLOUD_CLIENT_SECRET=TspMXEFoJw0vfw76DvcfXo9wnwcPrPq2

# VK API
VK_CLIENT_ID=GlFWm56_4fj_mz46rlArh9490HkyQYpaA
VK_CLIENT_SECRET=

# Прокси
PROXY_URL=http://127.0.0.1:8888

# Анти-цензура
PREFER_ORIGINAL=True
AUTO_REPLACE_CENSORED=True
```

**Пример frontend/.env:**
```env
VITE_API_URL=http://localhost:8081/api
```

---

## 🔧 ЭТАП 4: УСТАНОВКА ЗАВИСИМОСТЕЙ

### 4.1. Backend зависимости

```bash
cd ~/projects/music-app/backend

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Проверка установки
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

### 4.2. Frontend зависимости

```bash
cd ~/projects/music-app/frontend

# Установка Node.js зависимостей
npm install

# Проверка установки
npm list react vite
```

---

## 🗄️ ЭТАП 5: ВОССТАНОВЛЕНИЕ БАЗЫ ДАННЫХ

### 5.1. Импорт MongoDB (если есть бэкап)

```bash
# Если вы экспортировали базу на старом ПК
mongorestore --uri="mongodb://localhost:27017" --db=ultimate_music_app /путь/к/backup/mongodb/ultimate_music_app

# Проверка
mongosh
> use ultimate_music_app
> show collections
> db.users.countDocuments()
> exit
```

### 5.2. Инициализация Redis

```bash
# Проверка работы Redis
redis-cli ping
# Должно вернуть: PONG

# Если есть бэкап - копируем dump.rdb
# sudo cp /путь/к/backup/redis/dump.rdb /var/lib/redis/
# sudo systemctl restart redis
```

---

## 🎵 ЭТАП 6: ВОССТАНОВЛЕНИЕ МУЗЫКАЛЬНОЙ БИБЛИОТЕКИ

```bash
# Если у вас есть бэкап библиотеки
cd ~/projects/music-app/backend
tar -xzvf /путь/к/music_library_backup.tar.gz

# Или скопируйте папку вручную
# cp -r /старый/путь/music_library/ ./music_library/

# Проверка
ls -la music_library/
```

---

## 🚀 ЭТАП 7: ЗАПУСК ПРОЕКТА

### 7.1. Тестовый запуск

**Backend:**
```bash
cd ~/projects/music-app/backend
source venv/bin/activate

# Проверка конфигурации
python -c "from config import settings; print(settings.dict())"

# Запуск сервера
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка:**
```bash
curl http://localhost:8000/health
```

**Frontend (разработка):**
```bash
cd ~/projects/music-app/frontend

# Запуск dev сервера
npm run dev
```

### 7.2. Production запуск

**Создание systemd сервисов:**

```bash
# Backend сервис
sudo nano /etc/systemd/system/music-app-backend.service
```

```ini
[Unit]
Description=Ultimate Music App Backend
After=network.target mongod.service redis.service

[Service]
User=ваш_пользователь
WorkingDirectory=/home/ваш_пользователь/projects/music-app/backend
Environment="PATH=/home/ваш_пользователь/projects/music-app/backend/venv/bin"
ExecStart=/home/ваш_пользователь/projects/music-app/backend/venv/bin/python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# CORS Proxy сервис
sudo nano /etc/systemd/system/music-app-cors.service
```

```ini
[Unit]
Description=Ultimate Music App CORS Proxy
After=network.target music-app-backend.service

[Service]
User=ваш_пользователь
WorkingDirectory=/home/ваш_пользователь/projects/music-app/backend
Environment="PATH=/home/ваш_пользователь/projects/music-app/backend/venv/bin"
ExecStart=/home/ваш_пользователь/projects/music-app/backend/venv/bin/python cors_proxy_8081.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Включение и запуск сервисов
sudo systemctl daemon-reload
sudo systemctl enable music-app-backend
sudo systemctl enable music-app-cors
sudo systemctl start music-app-backend
sudo systemctl start music-app-cors

# Проверка статуса
sudo systemctl status music-app-backend
sudo systemctl status music-app-cors
```

---

## 🌐 ЭТАП 8: НАСТРОЙКА HTTPS (ОПЦИОНАЛЬНО)

### Вариант 1: Cloudflare Tunnel (как на текущем ПК)

```bash
# Установка cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Быстрый запуск
cloudflared tunnel --url http://localhost:8081
```

### Вариант 2: Nginx + Let's Encrypt

```bash
# Установка Nginx
sudo apt install -y nginx

# Конфигурация
sudo nano /etc/nginx/sites-available/music-app
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Включение сайта
sudo ln -s /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# HTTPS через Certbot
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ✅ ЭТАП 9: ПРОВЕРКА РАБОТЫ

### Чеклист

```bash
# 1. Проверка MongoDB
mongosh --eval "db.adminCommand('ping')"

# 2. Проверка Redis
redis-cli ping

# 3. Проверка Backend
curl http://localhost:8000/health

# 4. Проверка CORS Proxy
curl http://localhost:8081/api/censorship/test

# 5. Проверка Frontend
# Откройте в браузере http://localhost:5173

# 6. Проверка поиска треков
curl "http://localhost:8000/api/search?q=eminem&limit=5"

# 7. Проверка Anti-Censorship
curl "http://localhost:8000/api/censorship/test"
```

---

## 🔧 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: Ошибка подключения к MongoDB

**Решение:**
```bash
# Проверка статуса MongoDB
sudo systemctl status mongod

# Если не запущен
sudo systemctl start mongod

# Проверка логов
sudo tail /var/log/mongodb/mongod.log
```

### Проблема 2: Ошибка импортов Python

**Решение:**
```bash
cd ~/projects/music-app/backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Проблема 3: CORS ошибки в браузере

**Решение:**
- Убедитесь, что CORS proxy запущен на порту 8081
- Проверьте `VITE_API_URL` в frontend/.env

### Проблема 4: Не работает поиск музыки

**Решение:**
- Проверьте прокси (если нужен)
- Проверьте API ключи в .env
- Проверьте логи: `tail -f /tmp/server.log`

---

## 📊 СРАВНЕНИЕ КОНФИГУРАЦИЙ

| Параметр | Старый ПК | Новый ПК |
|----------|-----------|----------|
| ОС | Linux | (ваша) |
| Python | 3.12 | (установить) |
| Node.js | 20.x | (установить) |
| MongoDB | localhost:27017 | localhost:27017 |
| Redis | localhost:6379 | localhost:6379 |
| Backend порт | 8000 | 8000 |
| CORS Proxy порт | 8081 | 8081 |
| HTTPS | Cloudflare Tunnel | (настроить) |

---

## 🎯 МИНИМАЛЬНАЯ КОНФИГУРАЦИЯ ДЛЯ РАЗРАБОТКИ

Если хотите быстро начать без полной настройки:

```bash
# Только Backend (без MongoDB и Redis)
cd ~/projects/music-app/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск в режиме разработки
export DEBUG=True
export MONGODB_URL=""  # Пусто - режим без БД
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

---

## 📝 ЧЕКЛИСТ ПЕРЕНOSА

- [ ] Закоммитить все изменения в Git
- [ ] Сделать push в GitHub
- [ ] Сохранить .env файлы (скопировать содержимое)
- [ ] Экспортировать MongoDB (опционально)
- [ ] Установить Python 3.9+ на новом ПК
- [ ] Установить Node.js 18+ на новом ПК
- [ ] Установить MongoDB
- [ ] Установить Redis
- [ ] Клонировать репозиторий
- [ ] Создать .env файлы с правильными значениями
- [ ] Установить backend зависимости (pip)
- [ ] Установить frontend зависимости (npm)
- [ ] Импортировать базу данных
- [ ] Запустить backend
- [ ] Запустить frontend
- [ ] Проверить работу API
- [ ] Настроить HTTPS (опционально)

---

## 📞 ПОМОЩЬ

Если возникли проблемы:

1. Проверьте логи:
   ```bash
   tail -f /tmp/server.log
   tail -f /tmp/cors.log
   journalctl -u music-app-backend -f
   ```

2. Проверьте статус сервисов:
   ```bash
   sudo systemctl status mongod
   sudo systemctl status redis
   sudo systemctl status music-app-backend
   ```

3. Проверьте порты:
   ```bash
   ss -tlnp | grep -E '8000|8081|27017|6379'
   ```

---

**🎵 УДАЧНОГО ПЕРЕНOSА!**
