# 🌐 НАСТРОЙКА ultimatemusic.c6t.ru

## ✅ ВАШ ДОМЕН: ultimatemusic.c6t.ru

---

## 📋 ШАГ 1: НАСТРОЙКА DNS

### Зайдите туда где регистрировали домен

**Добавьте DNS записи:**

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| **A** | @ | 78.140.249.136 | Auto |
| **A** | www | 78.140.249.136 | Auto |

**Или CNAME:**

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| **CNAME** | @ | c6t.ru | Auto |

---

## 🔧 ШАГ 2: НАСТРОЙКА НА СЕРВЕРЕ

### 2.1 Конфигурация Nginx

**Выполните (нужен sudo/root):**

```bash
# Создайте конфиг
cat > /tmp/music-nginx.conf << 'EOF'
server {
    listen 80;
    server_name ultimatemusic.c6t.ru www.ultimatemusic.c6t.ru;
    
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

# Примените (нужен root!)
sudo cp /tmp/music-nginx.conf /etc/nginx/sites-available/music-app
sudo ln -sf /etc/nginx/sites-available/music-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

### 2.2 Проверка

```bash
# Должно работать
curl http://ultimatemusic.c6t.ru/
curl http://ultimatemusic.c6t.ru/api/health
```

---

## 🔒 ШАГ 3: HTTPS (если DNS работает)

**ВАЖНО:** DNS должен указывать на ваш сервер!

```bash
# Установка certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d ultimatemusic.c6t.ru -d www.ultimatemusic.c6t.ru \
  --non-interactive --agree-tos --email your-email@gmail.com
```

**Если работает - получите:**
```
✅ HTTPS настроен!
```

---

## 📱 ШАГ 4: TELEGRAM

**После настройки HTTPS:**

1. @BotFather → `/newapp`
2. URL: `https://ultimatemusic.c6t.ru`
3. Готово!

---

## 🎯 БЫСТРЫЙ СТАРТ (ПРЯМО СЕЙЧАС)

### Без HTTPS (работает сразу):

```
http://78.140.249.136:8000           - Бэкенд
http://78.140.249.136:8000/docs      - Swagger
http://78.140.249.136:8000/static/local-test.html - Тест
```

### С доменом (после настройки DNS):

```
http://ultimatemusic.c6t.ru          - Сайт
https://ultimatemusic.c6t.ru         - HTTPS (после certbot)
```

---

## ⚠️ ПРОБЛЕМЫ И РЕШЕНИЯ

### DNS не работает

**Подождите 5-60 минут** после изменения DNS записей.

**Проверка:**
```bash
ping ultimatemusic.c6t.ru
nslookup ultimatemusic.c6t.ru
```

### certbot не видит домен

**DNS должен указывать на ваш IP!**

```bash
# Проверка
curl ifconfig.me
# Должно быть: 78.140.249.136

# DNS должен показывать этот IP
ping ultimatemusic.c6t.ru
```

### Nginx не запускается

```bash
# Проверка конфига
sudo nginx -t

# Логи
sudo journalctl -u nginx -f
```

---

## 📊 АРХИТЕКТУРА

```
Пользователь
    │
    ▼
ultimatemusic.c6t.ru (DNS → 78.140.249.136)
    │
    ▼
Nginx (порт 80/443)
    │
    ├─ /          → /home/c1ten12/music-app/frontend/dist
    ├─ /api/*     → http://localhost:8000
    └─ /rest/*    → http://localhost:8000
```

---

## ✅ ЧЕКЛИСТ

- [ ] DNS настроен (A запись на 78.140.249.136)
- [ ] Nginx настроен (конфиг выше)
- [ ] HTTP работает (curl http://ultimatemusic.c6t.ru)
- [ ] HTTPS получен (certbot)
- [ ] Telegram настроен (@BotFather)

---

**🎵 НАЧНИТЕ С ШАГА 1 - НАСТРОЙТЕ DNS!**
