# 🎵 НАСТРОЙКА ПРИЛОЖЕНИЯ - YouTube Edition

**Версия:** 3.1.0  
**Основной источник:** YouTube ✅  
**SoundCloud:** Отложен на потом ⚠️

---

## ✅ Текущая конфигурация

### Работает:
- ✅ **YouTube** - поиск и стриминг
- ✅ **Anti-Censorship** - распознавание версий
- ✅ **Прокси** - обход блокировок
- ✅ **Фронтенд** - GitHub Pages

### Не работает (опционально):
- ⚠️ **SoundCloud** - требует OAuth
- ⚠️ **MongoDB** - для плейлистов

---

## 🚀 Быстрый старт

### 1. Запуск прокси

```bash
# В одном терминале
proxy --hostname 127.0.0.1 --port 8888 &
```

### 2. Запуск сервера

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### 3. Проверка

```bash
# Health check
curl http://localhost:8000/health

# Поиск треков
curl "http://localhost:8000/api/censorship/search-uncensored?q=adele"

# Anti-Censorship тест
curl http://localhost:8000/api/censorship/test
```

---

## 📡 API Endpoints

### Поиск музыки

```bash
# Поиск с explicit приоритетом
GET /api/censorship/search-uncensored?q={query}&prefer_explicit=true&limit=20

# Пример
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=eminem&prefer_explicit=true"
```

### Проверка на цензуру

```bash
# Проверка трека
GET /api/censorship/check?track_id={id}&source={source}

# Пример
curl "http://192.168.31.97:8000/api/censorship/check?track_id=test"
```

### Поиск оригинала

```bash
# Найти оригинальную версию
POST /api/censorship/find-original

# Пример
curl -X POST "http://192.168.31.97:8000/api/censorship/find-original" \
  -H "Content-Type: application/json" \
  -d '{"track_id": "test", "source": "youtube"}'
```

### Стриминг

```bash
# Получить аудио URL
GET /audio/stream/{video_id}

# Пример
curl "http://192.168.31.97:8000/audio/stream/dQw4w9WgXcQ"
```

---

## 🔧 Конфигурация (.env)

```env
# Сервер
HOST=0.0.0.0
PORT=8000

# Прокси (для обхода блокировок YouTube)
PROXY_URL=http://127.0.0.1:8888

# Основной источник
PRIMARY_SOURCE=youtube

# SoundCloud (отложено)
# SOUNDCLOUD_CLIENT_ID=gZX8jnL55gAHKRgcpIMt9nTUKo94Un61
# SOUNDCLOUD_CLIENT_SECRET=TspMXEFoJw0vfw76DvcfXo9wnwcPrPq2

# JWT
SECRET_KEY=dev-secret-key-not-for-production-min-32-chars-change-in-prod

# Анти-цензура
PREFER_ORIGINAL=True
AUTO_REPLACE_CENSORED=True
```

---

## 📊 Статус функционала

| Функция | Статус | Примечание |
|---------|--------|------------|
| **Поиск треков** | ✅ | YouTube работает |
| **Anti-Censorship** | ✅ | Все функции |
| **Распознавание версий** | ✅ | Clean/Explicit |
| **Поиск оригиналов** | ✅ | Fuzzy matching |
| **Прокси** | ✅ | HTTP прокси |
| **Аудио стриминг** | ⚠️ | Получение URL |
| **Плейлисты** | ❌ | Требуется MongoDB |
| **SoundCloud** | ⚠️ | Требуется OAuth |

---

## 🎯 Как использовать

### Поиск музыки

```bash
# Найти трек
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele hello"

# С фильтром explicit
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=eminem&prefer_explicit=true"
```

### Проверка на цензуру

```bash
# Проверить трек
curl "http://192.168.31.97:8000/api/censorship/check?track_id=abc"
```

### Получить аудио URL

```bash
# Для VLC или скачивания
curl "http://192.168.31.97:8000/audio/stream/{video_id}"
```

### Открыть приложение

```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

---

## 🛠️ Управление

### Запуск всего стека

```bash
# 1. Прокси
proxy --hostname 127.0.0.1 --port 8888 &

# 2. Сервер
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### Остановка

```bash
pkill -f "proxy --hostname"
pkill -f "uvicorn main_lite"
```

### Перезапуск

```bash
# Перезапуск сервера
pkill -f "uvicorn main_lite"
sleep 2
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

---

## 📝 Планы на будущее

### SoundCloud (потом)

1. Пройти OAuth авторизацию
2. Получить access token
3. Добавить в `.env`
4. Включить как дополнительный источник

### MongoDB (потом)

1. Установить MongoDB
2. Запустить: `docker run -d -p 27017:27017 mongo`
3. Переключиться на `main.py` вместо `main_lite.py`

### HTTPS (потом)

1. Установить Nginx
2. Получить SSL сертификат (Let's Encrypt)
3. Настроить proxy_pass

---

## 📄 Документация

- `README.md` - общая информация
- `DEPLOYMENT_COMPLETE.md` - отчёт о развёртывании
- `FINAL_REPORT.md` - финальный отчёт
- `PROXY_SETUP.md` - настройка прокси
- `AUDIO_STREAMING_STATUS.md` - стриминг
- `SOUNDCLOUD_YOUTUBE_STATUS.md` - статус источников

---

## 🎉 Готово!

**Приложение работает!**

- ✅ YouTube поиск
- ✅ Anti-Censorship
- ✅ Прокси
- ✅ Фронтенд

**SoundCloud и MongoDB можно добавить позже!**
