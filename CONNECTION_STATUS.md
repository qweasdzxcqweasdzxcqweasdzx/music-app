# ✅ СВЯЗЬ ФРОНТЕНД-БЭКЭНД РАБОТАЕТ!

## 📊 Текущий статус

| Компонент | Статус | URL |
|-----------|--------|-----|
| **Бэкенд** | ✅ **РАБОТАЕТ** | http://localhost:8000 |
| **CORS Proxy** | ✅ **РАБОТАЕТ** | http://localhost:8081 |
| **Frontend (GitHub)** | ⚠️ Cloudflare нестабилен | GitHub Pages |

---

## 🎯 Решение для тестирования

### Вариант 1: Локальная тестовая страница (РЕКОМЕНДУЕТСЯ)

Откройте в браузере:
```
http://localhost:8000/static/local-test.html
```

**Преимущества:**
- ✅ Всегда работает
- ✅ Прямое подключение к бэкенду
- ✅ Обход CORS через proxy
- ✅ Поиск и воспроизведение

---

### Вариант 2: Swagger UI (для API тестов)

```
http://localhost:8000/docs
```

Все API endpoints доступны с тестированием из браузера.

---

### Вариант 3: GitHub Pages + Cloudflare (для демонстрации)

```bash
cd /home/c1ten12/music-app
./fix-connection.sh
```

**Недостатки:**
- ⚠️ Cloudflare Quick Tunnel отключается каждые 5-15 минут
- ⚠️ Требуется постоянный перезапуск
- ⚠️ GitHub Pages обновляется с задержкой 1-2 минуты

---

## 🔧 Проверка связи

### Быстрая проверка:

```bash
# Бэкенд
curl http://localhost:8000/health

# CORS Proxy
curl http://localhost:8081/api/censorship/test

# Поиск треков
curl "http://localhost:8081/api/censorship/search-uncensored?q=eminem&limit=5"
```

### Скрипт проверки:

```bash
./check-connection.sh
```

---

## 📡 API Endpoints

### Через CORS Proxy (для браузера):
```
http://localhost:8081/api/censorship/search-uncensored?q=eminem
http://localhost:8081/api/censorship/test
http://localhost:8081/health
```

### Напрямую (для curl/scripts):
```
http://localhost:8000/api/censorship/search-uncensored?q=eminem
http://localhost:8000/api/censorship/test
http://localhost:8000/health
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│  Браузер                                            │
│  - GitHub Pages (нестабильно)                       │
│  - local-test.html (рекомендуется)                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  CORS Proxy (порт 8081)                             │
│  Python FastAPI - обход CORS                        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  Backend API (порт 8000)                            │
│  FastAPI + yt-dlp + SoundCloud                      │
│  - Anti-Censorship System                           │
│  - Audio Streaming                                  │
│  - Multi-platform Search                            │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Команды для работы

### Запустить всё:

```bash
# 1. Бэкенд (если не запущен)
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000

# 2. CORS Proxy (новое окно)
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python cors_proxy_8081.py

# 3. Открыть тестовую страницу
# http://localhost:8000/static/local-test.html
```

### Проверить процессы:

```bash
ps aux | grep -E "(uvicorn|cors_proxy)" | grep -v grep
```

### Перезапустить Cloudflare (если нужен для демонстрации):

```bash
./fix-connection.sh
```

---

## 📝 Примечания

1. **Локальная тестовая страница** (`/static/local-test.html`) - лучшее решение для разработки
2. **Cloudflare Quick Tunnel** - только для кратковременных демонстраций
3. **Для продакшена** используйте постоянный Cloudflare Tunnel или Nginx + HTTPS

---

## 🔗 Ссылки

| Ресурс | URL |
|--------|-----|
| Local Test Page | http://localhost:8000/static/local-test.html |
| Swagger UI | http://localhost:8000/docs |
| GitHub Pages | https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/ |
| Логи сервера | `tail -f /tmp/server.log` |
| Логи CORS | `tail -f /tmp/cors.log` |

---

**✅ СВЯЗЬ РАБОТАЕТ! Используйте локальную тестовую страницу для стабильной работы.**
