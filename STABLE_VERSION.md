# 🎵 STABLE VERSION - Стабильная версия для Telegram

## ✅ Текущий статус

| Компонент | Статус | URL |
|-----------|--------|-----|
| **Бэкенд** | ✅ РАБОТАЕТ | http://localhost:8000 |
| **CORS Proxy** | ✅ РАБОТАЕТ | http://localhost:8081 |
| **Cloudflare Quick Tunnel** | ⚠️ Нестабилен | Отключается каждые 5-15 мин |

---

## 🚀 Быстрый запуск

```bash
cd /home/c1ten12/music-app
./stable-run.sh
```

---

## 📱 Решение для Telegram

### Проблема
Telegram требует HTTPS для Mini Apps. Cloudflare Quick Tunnel (бесплатный) нестабилен.

### Решение 1: Локальное тестирование (рекомендуется для разработки)

1. Откройте в браузере:
   ```
   http://localhost:8000/static/local-test.html
   ```

2. Для тестирования Telegram WebApp SDK используйте:
   - [Telegram WebApp Mock](https://web.telegram.org/k/)
   - Или реальное устройство с включенной отладкой

### Решение 2: Ngrok (стабильнее Cloudflare)

```bash
# Установка ngrok (если не установлен)
cd /tmp
curl -sLO https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
mv ngrok /home/c1ten12/bin/

# Настройка токена (получите на https://dashboard.ngrok.com)
/home/c1ten12/bin/ngrok config add-authtoken YOUR_TOKEN

# Запуск
/home/c1ten12/bin/ngrok http 8081
```

Получите стабильный HTTPS URL для Telegram.

### Решение 3: Cloudflare Named Tunnel (для продакшена)

Требуется домен:

```bash
./setup-stable-tunnel.sh
```

---

## 🔧 Команды управления

| Команда | Описание |
|---------|----------|
| `./stable-run.sh` | Запуск всех сервисов |
| `./stop.sh` | Остановка всех сервисов |
| `./status.sh` | Проверка статуса |
| `./check-connection.sh` | Проверка связи |

---

## 📡 Проверка работы

### Локальная проверка (всегда работает):

```bash
# Бэкенд
curl http://localhost:8000/health

# CORS Proxy
curl http://localhost:8081/api/censorship/test

# Поиск
curl "http://localhost:8081/api/censorship/search-uncensored?q=eminem"

# Локальная страница
curl http://localhost:8000/static/local-test.html
```

### Swagger UI:
```
http://localhost:8000/docs
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│  Клиент                                             │
│  - Браузер (локально)                               │
│  - Telegram Mini App                                │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS (ngrok/Cloudflare)
                   ▼
┌─────────────────────────────────────────────────────┐
│  HTTPS Tunnel                                       │
│  - Cloudflare Quick Tunnel (нестабилен)             │
│  - Ngrok (стабильнее)                               │
│  - Cloudflare Named Tunnel (продакшен)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  CORS Proxy (порт 8081)                             │
│  Обход CORS политик                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Backend API (порт 8000)                            │
│  FastAPI + yt-dlp + SoundCloud                      │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Настройка Telegram Mini App

### 1. Получите HTTPS URL

Используйте ngrok (рекомендуется):

```bash
/home/c1ten12/bin/ngrok http 8081
```

Скопируйте URL (например: `https://abc123.ngrok.io`)

### 2. Создайте бота

1. @BotFather → `/newbot`
2. @BotFather → `/newapp`
3. Вставьте HTTPS URL

### 3. Обновите фронтенд

```javascript
// frontend/src/api/musicApi.js
const API_URL = 'https://abc123.ngrok.io/api';
```

### 4. Соберите и запушите

```bash
cd /home/c1ten12/music-app/frontend
npm run build
cd ..
git add -f frontend/dist
git commit -m "Update for Telegram"
git push origin main
```

---

## 🛠️ Troubleshooting

### Cloudflare отключается

Это нормально для Quick Tunnel. Используйте ngrok или Named Tunnel.

### CORS ошибки в браузере

Убедитесь что CORS proxy работает:
```bash
curl http://localhost:8081/api/censorship/test
```

### Telegram не открывает приложение

Проверьте:
1. URL должен быть HTTPS
2. URL должен быть валидным
3. Бот должен иметь доступ к Mini App

---

## 📊 Логи

```bash
# Бэкенд
tail -f /tmp/music-app/backend.log

# CORS Proxy
tail -f /tmp/music-app/cors.log

# Cloudflare
tail -f /tmp/music-app/cloudflared.log

# Systemd (если установлено)
journalctl -u music-app-backend -f
```

---

## 🎯 Чеклист готовности

- [ ] Бэкенд запущен (`./stable-run.sh`)
- [ ] CORS Proxy работает
- [ ] HTTPS туннель настроен (ngrok/Cloudflare)
- [ ] Фронтенд обновлён с правильным URL
- [ ] Telegram бот создан
- [ ] Mini App настроен в @BotFather
- [ ] Тест в Telegram пройден

---

## 🔗 Ссылки

- [Telegram WebApp SDK](https://core.telegram.org/bots/webapps)
- [Ngrok](https://ngrok.com)
- [Cloudflare Tunnels](https://www.cloudflare.com/products/tunnel/)

---

**✅ ГОТОВО!**

Для локального тестирования: `http://localhost:8000/static/local-test.html`

Для Telegram: настройте ngrok и обновите URL в фронтенде.
