# 🔧 Связь Фронтенд-Бэкенд - Решение

## ✅ Текущий статус

| Компонент | Статус | URL/Порт |
|-----------|--------|----------|
| **Бэкенд** | ✅ Работает | http://localhost:8000 |
| **CORS Proxy** | ✅ Работает | http://localhost:8081 |
| **Cloudflare Tunnel** | ⚠️ Нестабилен | Quick Tunnel |

---

## 🚀 Быстрое решение

### Вариант 1: Локальное тестирование (рекомендуется для разработки)

Откройте в браузере напрямую:
```
http://localhost:8000/docs
```

Swagger UI покажет все доступные API endpoints.

### Вариант 2: Использование Cloudflare (для демонстрации)

```bash
cd /home/c1ten12/music-app
./fix-connection.sh
```

**Важно:** Cloudflare Quick Tunnel может отключаться каждые 5-15 минут.

---

## 📡 API Endpoints для проверки

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Тест Anti-Censorship
curl http://localhost:8081/api/censorship/test

# Поиск треков
curl "http://localhost:8081/api/censorship/search-uncensored?q=eminem&limit=5"

# Получение аудио URL
curl "http://localhost:8000/audio/stream/dQw4w9WgXcQ"
```

---

## 🔧 Если Cloudflare отключился

### Быстрый перезапуск:

```bash
# 1. Убить старый процесс
pkill -f cloudflared

# 2. Запустить новый
/home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081 &

# 3. Получить новый URL (появится через 5-10 секунд)
# Скопировать URL вида: https://xxxx-xxxx-xxxx.trycloudflare.com

# 4. Обновить фронтенд
cd /home/c1ten12/music-app/frontend/src/api
# Заменить URL в musicApi.js и Search.jsx

# 5. Собрать и запушить
cd /home/c1ten12/music-app/frontend
npm run build
cd ..
git add -f frontend/dist frontend/src/api/musicApi.js frontend/src/pages/Search.jsx
git commit -m "Update Cloudflare URL"
git push origin main
```

### Или использовать автоскрипт:

```bash
./fix-connection.sh
```

---

## 🏗️ Архитектура подключения

```
┌─────────────────────────────────────────┐
│  Фронтенд (GitHub Pages)                │
│  React App                              │
└──────────────┬──────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│  Cloudflare Tunnel (нестабилен)         │
│  https://xxx.trycloudflare.com          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  CORS Proxy (порт 8081)                 │
│  Python FastAPI                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend API (порт 8000)                │
│  FastAPI + yt-dlp + SoundCloud          │
└─────────────────────────────────────────┘
```

---

## 📊 Проверка связи

### Локальная проверка (всегда работает):

```bash
# Бэкенд
curl http://localhost:8000/health

# CORS Proxy
curl http://localhost:8081/api/censorship/test
```

### Через Cloudflare (может не работать):

```bash
# Получить текущий URL из musicApi.js
grep API_URL /home/c1ten12/music-app/frontend/src/api/musicApi.js

# Проверить
curl https://YOUR-URL.trycloudflare.com/api/censorship/test
```

---

## 🛠️ Постоянное решение (для продакшена)

### 1. Создать постоянный Cloudflare Tunnel:

```bash
# Залогиниться в Cloudflare
cloudflared tunnel login

# Создать туннель
cloudflared tunnel create music-app

# Настроить маршрут
cloudflared tunnel route dns music-app your-domain.com

# Запустить
cloudflared tunnel run music-app
```

### 2. Настроить Nginx + HTTPS:

```bash
# Установить Nginx
sudo apt install nginx

# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com

# Настроить прокси
sudo nano /etc/nginx/sites-available/music-app
```

### 3. Настроить systemd сервис:

```ini
# /etc/systemd/system/music-app.service
[Unit]
Description=Music App Backend
After=network.target

[Service]
User=c1ten12
WorkingDirectory=/home/c1ten12/music-app/backend
Environment="PATH=/home/c1ten12/music-app/backend/venv/bin"
ExecStart=/home/c1ten12/music-app/backend/venv/bin/python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📝 Примечания

1. **Cloudflare Quick Tunnel** - бесплатное решение для тестирования, не для продакшена
2. **CORS Proxy** необходим для обхода CORS политик браузера
3. **GitHub Pages** обновляется с задержкой 1-2 минуты после push

---

## 🔗 Ссылки

- Frontend: https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
- Backend Swagger: http://localhost:8000/docs
- Логи Cloudflare: `tail -f /tmp/cf.txt`
- Логи сервера: `tail -f /tmp/server.log`
