# 🚀 Развёртывание на собственном сервере

**Полная инструкция по хостингу и разработке на сервере**

## 📋 Требования

- VPS сервер (Ubuntu 22.04)
- Домен (опционально)
- SSH доступ

## 🖥️ 1. Аренда сервера

### Рекомендуемые провайдеры

| Провайдер | Цена | RAM | CPU | Disk |
|-----------|------|-----|-----|------|
| Timeweb Cloud | 150₽/мес | 2GB | 1 core | 20GB |
| Selectel | 200₽/мес | 2GB | 1 core | 20GB |
| Aeza | 100₽/мес | 2GB | 1 core | 20GB |

### Заказ сервера

1. Зарегистрироваться у провайдера
2. Создать VPS с Ubuntu 22.04
3. Получить IP адрес и root пароль
4. Записать данные!

## 🔌 2. Подключение к серверу

### Windows (PowerShell)
```powershell
ssh root@your-server-ip
# Ввести пароль
```

### Linux/Mac
```bash
ssh root@your-server-ip
# Ввести пароль
```

### VS Code Remote SSH (рекомендуется)
1. Установить расширение "Remote - SSH"
2. F1 → "Remote-SSH: Connect to Host"
3. Ввести: `root@your-server-ip`
4. Ввести пароль
5. ✅ Теперь работаете как с локальным проектом!

## 📦 3. Установка зависимостей

```bash
# Обновление системы
apt update && apt upgrade -y

# Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y

# Git
apt install git -y

# Redis (для кэширования)
apt install redis-server -y

# MongoDB (для базы данных)
apt install mongodb -y

# Nginx (веб-сервер)
apt install nginx -y

# FFmpeg (для аудио конвертации)
apt install ffmpeg -y

# Проверка версий
python3 --version  # Python 3.11.x
node --version     # v18.x
npm --version      # 9.x
```

## 📁 4. Загрузка проекта

### Вариант A: Git clone
```bash
cd /var/www
git clone https://github.com/your-username/music-app.git
cd music-app
```

### Вариант B: SCP/SFTP
```bash
# С локального компьютера
scp -r ./музыкавтг root@server-ip:/var/www/music-app
```

### Вариант C: WinSCP/FileZilla
1. Подключиться по SFTP (порт 22)
2. Перетащить файлы в `/var/www/music-app`

## ⚙️ 5. Настройка бэкенда

```bash
cd /var/www/music-app/backend

# Создание виртуального окружения
python3 -m venv venv

# Активация
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
nano .env
```

**Редактирование .env:**
```env
SECRET_KEY=super-secret-key-change-in-production
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017
```

## 🎨 6. Настройка фронтенда

```bash
cd /var/www/music-app/frontend

# Установка зависимостей
npm install

# Настройка .env
echo "VITE_API_URL=https://your-domain.com/api" > .env

# Сборка для продакшена
npm run build

# Копирование в static
cp -r dist/* ../backend/static/
```

## 🌐 7. Настройка Nginx

```bash
nano /etc/nginx/sites-available/music-app
```

**Конфигурация:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Для Let's Encrypt SSL
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Для WebSocket (если нужен Jam Session)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /var/www/music-app/backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Активация:**
```bash
# Создание симлинка
ln -s /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/

# Проверка конфигурации
nginx -t

# Перезапуск Nginx
systemctl restart nginx
```

## 🔒 8. Настройка SSL (HTTPS)

```bash
# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение сертификата
certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
certbot renew --dry-run
```

## 🔧 9. Настройка systemd сервиса

```bash
nano /etc/systemd/system/music-app.service
```

**Service файл:**
```ini
[Unit]
Description=Telegram Music Mini App
After=network.target redis.service mongodb.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/music-app/backend
Environment="PATH=/var/www/music-app/backend/venv/bin"
ExecStart=/var/www/music-app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Логи
StandardOutput=journal
StandardError=journal
SyslogIdentifier=music-app

[Install]
WantedBy=multi-user.target
```

**Запуск:**
```bash
# Перезагрузка systemd
systemctl daemon-reload

# Включение автозапуска
systemctl enable music-app

# Запуск
systemctl start music-app

# Проверка статуса
systemctl status music-app

# Просмотр логов
journalctl -u music-app -f
```

## 🧪 10. Проверка работы

```bash
# Проверка что сервис работает
curl http://localhost:8000/health

# Проверка через домен
curl https://your-domain.com/health

# Проверка фронтенда
curl https://your-domain.com
```

**Открыть в браузере:**
- https://your-domain.com
- https://your-domain.com/docs (API документация)

## 💻 11. Разработка на сервере

### VS Code Remote SSH (рекомендуется)

1. **Установка расширения:**
   - VS Code → Extensions → "Remote - SSH"

2. **Подключение:**
   - F1 → "Remote-SSH: Connect to Host"
   - Ввести: `root@your-server-ip`
   - Ввести пароль

3. **Открыть проект:**
   - File → Open Folder → `/var/www/music-app`

4. **Теперь можно:**
   - ✅ Редактировать файлы
   - ✅ Запускать терминал
   - ✅ Использовать Git
   - ✅ Отлаживать код

### Редактирование через терминал

```bash
# nano (проще)
nano /var/www/music-app/backend/main.py

# vim (сложнее но мощнее)
vim /var/www/music-app/backend/main.py

# Сохранение в nano: Ctrl+O, Enter, Exit: Ctrl+X
```

### Автоматическая перезагрузка

```bash
# В development режиме
cd /var/www/music-app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Изменения применяются автоматически!
```

### Git workflow на сервере

```bash
cd /var/www/music-app

# Внести изменения
nano backend/main.py

# Проверка
git status

# Commit
git add .
git commit -m "Fix bug"

# Push
git push origin main

# Перезапуск сервиса
systemctl restart music-app
```

## 📊 12. Мониторинг

```bash
# Логи приложения
journalctl -u music-app -f

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Использование ресурсов
htop
df -h
free -h

# Статус сервисов
systemctl status music-app
systemctl status nginx
systemctl status redis
systemctl status mongodb
```

## 🔧 13. Обновление проекта

```bash
cd /var/www/music-app

# Pull изменений из git
git pull origin main

# Установка новых зависимостей
cd backend
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
npm run build
cp -r dist/* ../backend/static/

# Перезапуск
systemctl restart music-app
```

## 🐛 14. Troubleshooting

### Сервис не запускается
```bash
systemctl status music-app
journalctl -u music-app -f
```

### Ошибка 502 Bad Gateway
```bash
# Проверить что backend работает
systemctl status music-app

# Проверить логи
journalctl -u music-app -f

# Проверить Nginx
nginx -t
systemctl status nginx
```

### Нет доступа к файлам
```bash
# Исправить права
chown -R www-data:www-data /var/www/music-app
chmod -R 755 /var/www/music-app
```

### Закончилось место
```bash
# Проверить место
df -h

# Очистить кэш
apt clean
journalctl --vacuum-time=1d
```

## 📈 15. Оптимизация

### Gunicorn вместо uvicorn (для продакшена)

```bash
pip install gunicorn

# В systemd service заменить на:
ExecStart=/var/www/music-app/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120
```

### Redis кэширование

```bash
# В .env добавить
REDIS_URL=redis://localhost:6379

# Перезапустить
systemctl restart music-app
```

### MongoDB индексы

```bash
mongosh

use music_app

db.tracks.createIndex({ title: 1, artist: 1 })
db.users.createIndex({ telegram_id: 1 }, { unique: true })
db.play_history.createIndex({ user_id: 1, played_at: -1 })
```

## ✅ Чеклист готовности

- [x] Сервер арендован
- [x] Зависимости установлены
- [x] Проект загружен
- [x] .env настроен
- [x] Фронтенд собран
- [x] Nginx настроен
- [x] SSL установлен
- [x] systemd сервис работает
- [x] HTTPS работает
- [x] Логи настроены

---

**Проект успешно развёрнут!** 🚀

**Для разработки:** Используйте VS Code Remote SSH  
**Для обновления:** `git pull && systemctl restart music-app`
