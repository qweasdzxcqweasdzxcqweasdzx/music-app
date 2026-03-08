# 🚀 DEPLOYMENT GUIDE

Полное руководство по развёртыванию **Ultimate Music App** с Anti-Censorship системой.

---

## 📋 Оглавление

1. [Архитектура](#архитектура)
2. [Требования к серверу](#требования-к-серверу)
3. [Быстрый старт](#быстрый-старт)
4. [Установка и настройка](#установка-и-настройка)
5. [Запуск сервера](#запуск-сервера)
6. [Настройка фронтенда](#настройка-фронтенда)
7. [API документация](#api-документация)
8. [Мониторинг и логи](#мониторинг-и-логи)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Pages                         │
│  https://yourusername.github.io/music-app/             │
│  (Frontend - React 19, Vite)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS API Calls
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Ваш сервер (VPS/Local)                     │
│  http://SERVER_IP:8000                                 │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Ultimate Music App Backend (FastAPI)            │ │
│  │  ├─ Anti-Censorship System ✓                     │ │
│  │  ├─ YouTube (yt-dlp)                             │ │
│  │  ├─ SoundCloud API                               │ │
│  │  └─ Fuzzy Matching Engine                        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Требования к серверу

### Минимальные

- **CPU:** 1 ядро
- **RAM:** 512 MB
- **Disk:** 5 GB
- **OS:** Ubuntu 20.04+ / Debian 11+

### Рекомендуемые

- **CPU:** 2 ядра
- **RAM:** 1 GB
- **Disk:** 10 GB
- **OS:** Ubuntu 22.04 LTS

---

## ⚡ Быстрый старт

### 1. Клонирование проекта

```bash
cd /home/c1ten12/music-app/backend
```

### 2. Активация окружения

```bash
source venv/bin/activate
```

### 3. Запуск сервера

```bash
# В фоновом режиме
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &

# Или в foreground (для отладки)
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### 4. Проверка

```bash
curl http://localhost:8000/health
```

---

## 🔧 Установка и настройка

### Шаг 1: Проверка Python

```bash
python3 --version
# Должно быть Python 3.9+
```

### Шаг 2: Создание виртуального окружения (если нет)

```bash
cd /home/c1ten12/music-app/backend
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Дополнительно для YouTube
pip install yt-dlp
```

### Шаг 4: Настройка .env (опционально)

```bash
cp .env.example .env
nano .env
```

**Минимальная конфигурация:**

```env
# Server
HOST=0.0.0.0
PORT=8000

# SoundCloud (для поиска музыки)
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret

# JWT
SECRET_KEY=your-secret-key-min-32-characters-long
```

**Опционально:**

```env
# Telegram Bot (для Mini App)
TELEGRAM_BOT_TOKEN=your_bot_token

# Proxy (для обхода ограничений)
PROXY_URL=http://proxy:port

# AI Services
SUNO_API_KEY=
MUBERT_TOKEN=
```

---

## 🚀 Запуск сервера

### Вариант 1: Systemd сервис (рекомендуется)

Создайте файл `/etc/systemd/system/music-app.service`:

```ini
[Unit]
Description=Ultimate Music App Backend
After=network.target

[Service]
Type=simple
User=c1ten12
WorkingDirectory=/home/c1ten12/music-app/backend
Environment="PATH=/home/c1ten12/music-app/backend/venv/bin"
ExecStart=/home/c1ten12/music-app/backend/venv/bin/python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Запуск:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable music-app
sudo systemctl start music-app
sudo systemctl status music-app
```

### Вариант 2: Screen/Tmux

```bash
# Установка screen
sudo apt install screen  # Ubuntu/Debian

# Создание сессии
screen -S music-app

# Запуск сервера
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000

# Отсоединение: Ctrl+A, D
# Подключение: screen -r music-app
```

### Вариант 3: Nohup (простой)

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &

# Проверка
ps aux | grep uvicorn
tail -f /tmp/uvicorn.log
```

### Вариант 4: PM2 (продвинутый)

```bash
# Установка PM2
npm install -g pm2

# Запуск
cd /home/c1ten12/music-app/backend
source venv/bin/activate
pm2 start "python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000" --name music-app

# Управление
pm2 status
pm2 logs music-app
pm2 restart music-app
pm2 save
```

---

## 🌐 Настройка фронтенда

### 1. Обновление API URL во фронтенде

В файле `frontend/src/api/musicApi.js` (или аналогичном):

```javascript
// Было (localhost)
const API_URL = 'http://localhost:8000/api';

// Стало (ваш сервер)
const API_URL = 'http://YOUR_SERVER_IP:8000/api';

// Или с HTTPS (рекомендуется)
const API_URL = 'https://your-domain.com/api';
```

### 2. Настройка CORS (уже настроено)

В `main_lite.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена укажите конкретные домены
    # allow_origins=["https://yourusername.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Деплой фронтенда на GitHub Pages

```bash
cd /home/c1ten12/music-app/frontend

# Обновление API URL
nano src/api/musicApi.js  # Измените API_URL на ваш сервер

# Сборка
npm run build

# Деплой (если настроен)
git add dist/
git commit -m "Deploy to GitHub Pages"
git push
```

### 4. Проверка подключения

Откройте в браузере:

```
https://yourusername.github.io/music-app/
```

Или напрямую сервер:

```
http://YOUR_SERVER_IP:8000/docs
```

---

## 📡 API документация

### Основные endpoints

#### Health Check

```bash
GET http://YOUR_SERVER_IP:8000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "mongodb": "disabled (lite mode)",
  "youtube": "available",
  "soundcloud": "configured",
  "anti_censorship": "enabled"
}
```

#### Anti-Censorship

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/censorship/check` | GET | Проверка трека на цензуру |
| `/api/censorship/find-original` | POST | Поиск оригинальной версии |
| `/api/censorship/search-uncensored` | GET | Поиск с приоритетом explicit |
| `/api/censorship/analyze-batch` | POST | Массовый анализ треков |
| `/api/censorship/statistics` | GET | Статистика цензуры |
| `/api/censorship/replace-censored` | POST | Замена в плейлистах |

### Примеры использования

#### 1. Проверка трека

```bash
curl "http://YOUR_SERVER_IP:8000/api/censorship/check?track_id=123&source=soundcloud"
```

#### 2. Поиск оригинала

```bash
curl -X POST "http://YOUR_SERVER_IP:8000/api/censorship/find-original" \
  -H "Content-Type: application/json" \
  -d '{"track_id": "123", "source": "soundcloud"}'
```

#### 3. Поиск с explicit приоритетом

```bash
curl "http://YOUR_SERVER_IP:8000/api/censorship/search-uncensored?q=eminem&prefer_explicit=true&limit=10"
```

### Swagger UI

Откройте в браузере:

```
http://YOUR_SERVER_IP:8000/docs
```

---

## 📊 Мониторинг и логи

### Логи приложения

```bash
# Просмотр логов
tail -f /tmp/uvicorn.log

# Или через journalctl (для systemd)
sudo journalctl -u music-app -f
```

### Мониторинг процесса

```bash
# Проверка процесса
ps aux | grep uvicorn

# Проверка порта
netstat -tlnp | grep 8000
# или
ss -tlnp | grep 8000

# Проверка доступности
curl http://localhost:8000/health
```

### Логирование в файл

```bash
# Создание отдельного файла для логов
touch /var/log/music-app.log
chmod 644 /var/log/music-app.log

# Запуск с логированием
nohup python -m uvicorn main_lite:app \
  --host 0.0.0.0 \
  --port 8000 \
  >> /var/log/music-app.log 2>&1 &
```

---

## 🔒 Безопасность

### 1. Настройка Firewall

```bash
# Разрешение порта 8000
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status
```

### 2. HTTPS через Nginx (рекомендуется)

Установка Nginx:

```bash
sudo apt update
sudo apt install nginx
```

Конфигурация `/etc/nginx/sites-available/music-app`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🛠️ Troubleshooting

### Сервер не запускается

```bash
# Проверка логов
cat /tmp/uvicorn.log

# Проверка порта
sudo lsof -i :8000

# Проверка Python
which python3
python3 --version
```

### Ошибки импорта

```bash
# Переустановка зависимостей
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Проблемы с CORS

Ошибка в браузере:
```
Access to fetch at 'http://server:8000' from origin 'https://github.io' has been blocked by CORS policy
```

**Решение:** Убедитесь, что в `main_lite.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или ["https://yourusername.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### YouTube не работает

```bash
# Проверка yt-dlp
source venv/bin/activate
python -c "import yt_dlp; print(yt_dlp.version.__version__)"

# Обновление
pip install --upgrade yt-dlp
```

### SoundCloud не работает

Проверьте API ключи в `.env`:

```env
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
```

Получить ключи: https://soundcloud.com/you/apps

---

## 📈 Производительность

### Оптимизация

1. **Кэширование Redis** (опционально):

```bash
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

2. **Gunicorn + Uvicorn workers**:

```bash
pip install gunicorn

gunicorn main_lite:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

3. **Rate Limiting** (уже включено):

```python
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
```

---

## 🔄 Обновление

```bash
# Остановка сервера
sudo systemctl stop music-app  # или kill процесса

# Обновление кода
cd /home/c1ten12/music-app
git pull

# Обновление зависимостей
source venv/bin/activate
pip install -r backend/requirements.txt --upgrade

# Запуск
sudo systemctl start music-app
```

---

## 📞 Поддержка

### Файлы логов

- `/tmp/uvicorn.log` - логи сервера
- `/var/log/music-app.log` - логи (если настроено)
- `journalctl -u music-app` - systemd логи

### Диагностика

```bash
# Полный чеклист
echo "=== Python ===" && python3 --version
echo "=== Uvicorn ===" && which uvicorn
echo "=== yt-dlp ===" && yt-dlp --version
echo "=== Port 8000 ===" && ss -tlnp | grep 8000
echo "=== Health ===" && curl http://localhost:8000/health
```

---

## ✅ Чеклист развёртывания

- [ ] Клонирован репозиторий
- [ ] Создано виртуальное окружение
- [ ] Установлены зависимости
- [ ] Настроен `.env` (опционально)
- [ ] Сервер запущен и доступен
- [ ] Фронтенд обновлён с правильным API_URL
- [ ] Swagger UI доступен
- [ ] Health check проходит
- [ ] Настроен Firewall
- [ ] Настроено логирование
- [ ] Настроен автозапуск (systemd/pm2)

---

**Версия:** 3.1.0-lite  
**Последнее обновление:** 2026
