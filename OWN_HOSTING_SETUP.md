# 🚀 ПОЛНЫЙ СВОЙ ХОСТИНГ - ИНСТРУКЦИЯ

## ✅ ЧТО УЖЕ РАБОТАЕТ

| Компонент | Статус | URL |
|-----------|--------|-----|
| **Бэкенд** | ✅ Работает | http://localhost:8000 |
| **CORS Proxy** | ✅ Работает | http://localhost:8081 |
| **Nginx** | ✅ Установлен | http://localhost:80 |
| **Ваш IP** | ✅ | http://78.140.249.136 |

---

## 🔧 ЧТО НУЖНО СДЕЛАТЬ (нужен sudo)

### 1. Настройка Nginx

**Выполните от root/sudo:**

```bash
# Конфиг Nginx
cat > /etc/nginx/sites-available/music-app << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Фронтенд
    location / {
        root /home/c1ten12/music-app/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
    
    # Бэкенд API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # Subsonic API
    location /rest/ {
        proxy_pass http://localhost:8000/rest/;
        proxy_set_header Host $host;
    }
    
    # Статика
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }
}
EOF

# Включение
ln -sf /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/music-app
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

---

### 2. Проверка

```bash
# Должно работать:
curl http://78.140.249.136/
curl http://78.140.249.136/api/health
curl http://78.140.249.136/rest/ping.view
```

---

### 3. HTTPS (если есть домен)

**Если у вас есть домен (не субдомен!):**

```bash
# Установка certbot
apt install -y certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d your-domain.com -d www.your-domain.com

# Авто-обновление
certbot renew --dry-run
```

---

## 📱 ДЛЯ TELEGRAM

### Вариант 1: По IP (работает сейчас)

**URL для бота:**
```
http://78.140.249.136
```

⚠️ **Telegram требует HTTPS** для Mini Apps!

### Вариант 2: С доменом + HTTPS

1. Купите домен (от $5/год)
2. Настройте DNS на ваш IP: `78.140.249.136`
3. Получите HTTPS через certbot
4. Вставьте в Telegram: `https://your-domain.com`

### Вариант 3: Cloudflare Tunnel (бесплатно, нестабильно)

```bash
./start-cloudflare.sh
```

---

## 🎯 ПРЯМОЙ ДОСТУП СЕЙЧАС

### Без HTTPS (работает):

```
http://78.140.249.136:8000        - Бэкенд
http://78.140.249.136:8081        - CORS Proxy
http://78.140.249.136             - Nginx (нужно настроить)
```

### Локально (всегда работает):

```
http://localhost:8000
http://localhost:8081
http://localhost:8000/docs        - Swagger
http://localhost:8000/static/local-test.html  - Тестовая страница
```

---

## 🛠️ КОМАНДЫ

```bash
# Проверка что работает
curl http://localhost:8000/health
curl http://localhost:8081/api/censorship/test

# Перезапуск сервисов
pkill -f "uvicorn main_lite" && cd /home/c1ten12/music-app/backend && source venv/bin/activate && python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 &

# Статус
ps aux | grep -E "(nginx|uvicorn|cors)" | grep -v grep
```

---

## 📊 АРХИТЕКТУРА

```
Интернет
    │
    ▼
78.140.249.136:80 (Nginx)
    │
    ├─ /          → /home/c1ten12/music-app/frontend/dist
    ├─ /api/*     → http://localhost:8000
    ├─ /rest/*    → http://localhost:8000
    └─ /static/*  → http://localhost:8000
                        │
                        ├─ YouTube (yt-dlp)
                        └─ SoundCloud API
```

---

## ✅ МИНИМУМ ДЛЯ ЗАПУСКА

**Без Nginx, просто напрямую:**

1. Откройте браузер: `http://78.140.249.136:8000`
2. Или Swagger: `http://78.140.249.136:8000/docs`
3. Или тестовая страница: `http://78.140.249.136:8000/static/local-test.html`

**Для Telegram нужен HTTPS!**

---

## 🎯 РЕШЕНИЯ

| Проблема | Решение |
|----------|---------|
| **Нужен HTTPS для Telegram** | Купите домен + certbot |
| **Хочу бесплатно** | Cloudflare Tunnel (нестабильно) |
| **Хочу своё** | Nginx + домен + HTTPS |
| **Тестировать** | http://localhost:8000 |

---

## 📝 ИТОГ

**Сейчас работает:**
- ✅ Бэкенд: http://localhost:8000
- ✅ CORS Proxy: http://localhost:8081
- ✅ Nginx установлен (нужно настроить)

**Для Telegram:**
- ⚠️ Нужен HTTPS
- 📝 Купите домен (~$5-9/год)
- 🔒 Настройте certbot

**Полностью своё:**
- ✅ Сервер ваш
- ✅ Бэкенд ваш
- ✅ Фронтенд ваш
- ⚠️ Домен нужен для HTTPS

---

**ВЫПОЛНИТЕ КОМАНДЫ ИЗ РАЗДЕЛА 1 ДЛЯ НАСТРОЙКИ NGINX!**
