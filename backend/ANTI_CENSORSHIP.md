# 🚫 Anti-Censorship / Blues Detection System

Система для распознавания цензурированных (заблюренных) версий песен и поиска оригинальных (explicit) версий на разных площадках.

## 📋 Проблема

В России и некоторых других странах ввели цензуру на музыкальных платформах:
- Слова в песнях вырезают или заглушают (beep)
- Заменяют на более «безопасные» версии
- Названия треков могут отличаться на разных площадках

## ✨ Решение

Наш сервис автоматически:
1. **Распознает** цензурированные версии по маркерам в названии и metadata
2. **Ищет** оригинальные версии на YouTube, SoundCloud, VK, Navidrome
3. **Сравнивает** названия с помощью fuzzy matching (даже если они отличаются)
4. **Предлагает** замену для цензурных треков в плейлистах

---

## 🔧 Компоненты

### 1. Blues Detection Service

**Файл:** `services/blues_detection_service.py`

#### Основные возможности:

```python
from services.blues_detection_service import blues_detection_service

# Проверка на цензуру
is_censored = blues_detection_service.is_censored(track)

# Проверка на explicit версию
is_explicit = blues_detection_service.is_explicit_version(track)

# Определение типа версии: "explicit", "clean", "unknown"
version_type = blues_detection_service.get_version_type(track)

# Нормализация названия для сравнения
normalized = blues_detection_service.normalize_title("Bad Guy (Clean Version)")
# Результат: "bad guy"

# Коэффициент схожести названий (0.0 - 1.0)
similarity = blues_detection_service.similarity_ratio(
    "Bad Guy (Clean Version)",
    "Bad Guy (Explicit Original)"
)

# Поиск лучшего совпадения среди кандидатов
best_match = blues_detection_service.find_best_match(
    query_track,
    candidates,
    min_similarity=0.6
)

# Генерация поисковых запросов для поиска оригинала
queries = blues_detection_service.generate_search_queries(
    track,
    prefer_explicit=True
)

# Поиск оригинала на всех платформах
original = await blues_detection_service.find_original_version(censored_track)

# Отчет по цензуре в списке треков
report = blues_detection_service.get_censorship_report(tracks)
```

#### Маркеры для распознавания:

**Чистые версии (CENSOR_MARKERS):**
- `clean`, `radio edit`, `censored`, `edited`
- `версия`, `радио версия`, `цензурная`, `для эфира`

**Explicit версии (EXPLICIT_MARKERS):**
- `explicit`, `original`, `uncensored`, `dirty`
- `оригинал`, `нецензурная`, `полная версия`

---

### 2. YouTube Music Service (обновленный)

**Файл:** `services/youtube_service.py`

#### Новые методы:

```python
from services.youtube_service import YouTubeMusicService

yt = YouTubeMusicService()

# Поиск с приоритетом explicit
tracks = await yt.search(query, limit=20, prefer_explicit=True)

# Поиск оригинальной версии
original = await yt.get_original_track(query)

# Поиск нецензурированной версии для конкретного трека
uncensored = await yt.find_uncensored_version(censored_track)
```

---

## 📡 API Endpoints

### 1. Проверка трека на цензуру

```http
GET /api/censorship/check?track_id={id}&source={source}
```

**Пример:**
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

---

### 2. Поиск оригинальной версии

```http
POST /api/censorship/find-original
Content-Type: application/json

{
  "track_id": "123",
  "source": "soundcloud",
  "platforms": ["youtube", "soundcloud"]
}
```

**Ответ:**
```json
{
  "status": "found",
  "original_track": {
    "id": "yt_abc123",
    "title": "Bad Guy (Explicit Original)",
    "artist": "Billie Eilish",
    "source": "youtube",
    "is_explicit": true
  },
  "censored_track": {...},
  "similarity": 0.87
}
```

---

### 3. Поиск с приоритетом explicit

```http
GET /api/censorship/search-uncensored?q={query}&artist={artist}&prefer_explicit=true&limit=20
```

**Пример:**
```bash
curl "http://localhost:8000/api/censorship/search-uncensored?q=lose%20yourself&artist=Eminem&prefer_explicit=true"
```

**Ответ:**
```json
{
  "tracks": [
    {
      "track": {...},
      "is_censored": false,
      "is_explicit": true,
      "version_type": "explicit"
    }
  ],
  "total": 15,
  "explicit_count": 10,
  "censored_count": 5
}
```

---

### 4. Массовый анализ треков

```http
POST /api/censorship/analyze-batch
Content-Type: application/json

{
  "track_ids": ["id1", "id2", "id3"],
  "source": "soundcloud"
}
```

**Ответ:**
```json
{
  "summary": {
    "total_tracks": 3,
    "censored_count": 1,
    "explicit_count": 2,
    "censorship_percentage": 33.3
  },
  "tracks": [
    {
      "id": "id1",
      "title": "...",
      "is_censored": true,
      "is_explicit": false
    }
  ]
}
```

---

### 5. Статистика цензуры

```http
GET /api/censorship/statistics
```

**Ответ:**
```json
{
  "statistics": {
    "total_tracks": 100,
    "censored_count": 35,
    "explicit_count": 45,
    "censorship_percentage": 35.0
  },
  "analyzed_count": 100,
  "recommendation": "Используйте /censorship/find-original для поиска оригинальных версий"
}
```

---

### 6. Замена цензурных треков в плейлисте

```http
POST /api/censorship/replace-censored
Content-Type: application/json

{
  "track_ids": ["id1", "id2", "id3"]
}
```

**Ответ:**
```json
{
  "replacements": [
    {
      "original_id": "id1",
      "replacement": {
        "id": "yt_xyz789",
        "title": "Song (Explicit)",
        "artist": "Artist",
        "source": "youtube"
      },
      "reason": "censored_version"
    }
  ],
  "total_replacements": 1,
  "processed": 3
}
```

---

## 🧪 Тестирование

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python test_blues_simple.py
```

**Пример вывода:**
```
============================================================
Blues Detection Service - Тесты
============================================================

=== Тесты распознавания цензуры ===

✓ Clean track: Bad Guy (Clean Version)
  is_censored: True
  version_type: clean

✓ Explicit track: Bad Guy (Explicit Original)
  is_explicit: True
  version_type: explicit

=== Тесты Fuzzy Matching ===

Схожесть 'Bad Guy (Clean Version)' и 'Bad Guy (Explicit Original)': 0.47
Схожесть 'Bad Guy (Clean Version)' и 'Bad Guy - Radio Edit': 1.00

=== Тесты поисковых запросов ===

Сгенерированные запросы (12):
  1. Billie Eilish Bad Guy (Clean Version)
  2. Billie Eilish Bad Guy (Clean Version) explicit
  ...

============================================================
Все тесты завершены успешно!
============================================================
```

---

## 📊 Алгоритм работы

### 1. Распознавание цензуры

```
┌─────────────────────────────────────────────────────────┐
│  Трек: "Bad Guy (Clean Version)"                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Проверка маркеров:                                     │
│  - CENSOR_MARKERS: clean, radio edit, censored...       │
│  - EXPLICIT_MARKERS: explicit, original, uncensored...  │
│  - Маскированные слова: f***k, s[t]op...                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Результат: version_type = "clean"                      │
└─────────────────────────────────────────────────────────┘
```

### 2. Поиск оригинала

```
┌─────────────────────────────────────────────────────────┐
│  Цензурный трек: "Bad Guy (Clean Version)"              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Генерация запросов:                                    │
│  - "Billie Eilish Bad Guy explicit"                     │
│  - "Billie Eilish Bad Guy original"                     │
│  - "Billie Eilish Bad Guy uncensored"                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Поиск на платформах:                                   │
│  - YouTube → 10 треков                                  │
│  - SoundCloud → 8 треков                                │
│  - VK → 5 треков                                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Fuzzy Matching + фильтрация:                           │
│  - similarity > 0.6                                     │
│  - is_explicit = True                                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Найден оригинал: "Bad Guy (Explicit Original)"         │
│  similarity: 0.87                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Конфиденциальность

Система **не нарушает** авторские права:
- Поиск осуществляется через публичные API
- Пользователь сам выбирает версию для прослушивания
- Сервис仅提供 информацию о доступных версиях

---

## 🚀 Интеграция с фронтендом

### React компонент (пример)

```jsx
// components/ExplicitVersionFinder.jsx
import { useState } from 'react';

export function ExplicitVersionFinder({ track }) {
  const [original, setOriginal] = useState(null);
  const [loading, setLoading] = useState(false);

  const findOriginal = async () => {
    setLoading(true);
    const response = await fetch('/api/censorship/find-original', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        track_id: track.id,
        source: track.source
      })
    });
    const data = await response.json();
    if (data.status === 'found') {
      setOriginal(data.original_track);
    }
    setLoading(false);
  };

  return (
    <div>
      {track.is_censored && (
        <button onClick={findOriginal} disabled={loading}>
          {loading ? 'Поиск...' : 'Найти оригинальную версию'}
        </button>
      )}
      {original && (
        <div className="original-found">
          ✓ Найдено: {original.title}
        </div>
      )}
    </div>
  );
}
```

---

## 📝 Лицензия

MIT License

---

**v1.0** — Anti-Censorship System для Ultimate Music App
