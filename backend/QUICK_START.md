# 🚀 Quick Start - Anti-Censorship System

## ✅ Быстрый запуск (без MongoDB)

### 1. Активация виртуального окружения

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
```

### 2. Запуск сервера

```bash
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

Или в фоновом режиме:

```bash
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
```

### 3. Проверка работы

```bash
# Корневой endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Тест Anti-Censorship
curl http://localhost:8000/api/censorship/test
```

### 4. Swagger UI

Откройте в браузере: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### Anti-Censorship

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/censorship/check` | GET | Проверка трека на цензуру |
| `/api/censorship/find-original` | POST | Поиск оригинальной версии |
| `/api/censorship/search-uncensored` | GET | Поиск с приоритетом explicit |
| `/api/censorship/analyze-batch` | POST | Массовый анализ треков |
| `/api/censorship/statistics` | GET | Статистика цензуры |
| `/api/censorship/replace-censored` | POST | Замена в плейлистах |
| `/api/censorship/test` | GET | Тест системы |

---

## 🧪 Тесты

### Запуск тестов

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Простые тесты
python test_blues_simple.py

# Тест API endpoints
python test_api_endpoints.py
```

### Пример вывода тестов

```
======================================================================
Blues Detection Service - Тесты
======================================================================

✓ Clean track: Bad Guy (Clean Version)
  is_censored: True
  version_type: clean

✓ Explicit track: Bad Guy (Explicit Original)
  is_explicit: True
  version_type: explicit

======================================================================
✅ Все тесты завершены успешно!
======================================================================
```

---

## 🔧 Примеры запросов

### 1. Проверка трека

```bash
curl "http://localhost:8000/api/censorship/check?track_id=123&source=soundcloud"
```

**Ответ:**
```json
{
  "track_id": "123",
  "title": "Bad Guy (Clean Version)",
  "artist": "Billie Eilish",
  "is_censored": true,
  "is_explicit": false,
  "version_type": "clean",
  "confidence": 0.85
}
```

### 2. Поиск с приоритетом explicit

```bash
curl "http://localhost:8000/api/censorship/search-uncensored?q=eminem&prefer_explicit=true"
```

### 3. Поиск оригинальной версии

```bash
curl -X POST "http://localhost:8000/api/censorship/find-original" \
  -H "Content-Type: application/json" \
  -d '{"track_id": "123", "source": "soundcloud"}'
```

---

## 📦 Зависимости

Уже установлены:

- ✅ FastAPI
- ✅ Uvicorn
- ✅ yt-dlp (для YouTube)
- ✅ aiohttp (для HTTP запросов)

Опционально (для полной версии с MongoDB):

```bash
# MongoDB (не требуется для lite версии)
docker run -d -p 27017:27017 mongo:latest

# Redis (для кэширования)
docker run -d -p 6379:6379 redis:latest
```

---

## 🎯 Как это работает

### 1. Распознавание цензуры

```python
from services.blues_detection_service import blues_detection_service
from models import Track

track = Track(title="Bad Guy (Clean Version)", artist="Billie Eilish", ...)

is_censored = blues_detection_service.is_censored(track)
# True

version_type = blues_detection_service.get_version_type(track)
# "clean"
```

### 2. Fuzzy Matching

```python
# Нормализация названий
norm1 = blues_detection_service.normalize_title("Bad Guy (Clean Version)")
# "bad guy"

norm2 = blues_detection_service.normalize_title("Bad Guy (Explicit)")
# "bad guy explicit"

# Коэффициент схожести
similarity = blues_detection_service.similarity_ratio(
    "Bad Guy (Clean Version)",
    "Bad Guy (Explicit Original)"
)
# 0.47 - 1.0 (в зависимости от версий)
```

### 3. Поиск оригинала

```python
# Генерация поисковых запросов
queries = blues_detection_service.generate_search_queries(
    track,
    prefer_explicit=True
)
# ["Billie Eilish Bad Guy explicit", 
#  "Billie Eilish Bad Guy original",
#  "Billie Eilish Bad Guy uncensored", ...]

# Поиск на платформах
original = await blues_detection_service.find_original_version(censored_track)
```

---

## 📄 Документация

- **ANTI_CENSORSHIP.md** — полное описание системы
- **test_blues_simple.py** — юнит-тесты
- **test_api_endpoints.py** — тесты API endpoints

---

## ⚠️ Режимы работы

### Lite (текущий)

- ✅ Без MongoDB
- ✅ Без Redis
- ✅ Anti-Censorship система
- ✅ YouTube поиск (yt-dlp)
- ✅ SoundCloud (требуется API ключ)

### Full (требуется MongoDB)

```bash
# Запуск полной версии
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Требуется:
- MongoDB на `mongodb://localhost:27017`
- Redis на `redis://localhost:6379` (опционально)

---

## 🎉 Готово!

Сервер запущен и готов к использованию!

**Swagger UI:** http://localhost:8000/docs

**API тесты:**
```bash
curl http://localhost:8000/api/censorship/test
```
