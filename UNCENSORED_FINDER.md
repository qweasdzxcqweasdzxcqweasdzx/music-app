# 🎵 Uncensored Track Finder - Поиск оригинальных версий

## 📋 Описание

Система для поиска и переключения между цензурированными (clean/radio edit) и оригинальными (explicit/uncensored) версиями треков.

### Проблема
- В России и некоторых других странах ввели цензуру на музыкальных платформах
- Слова в песнях "блюрят" (заменяют, вырезают, заглушают)
- Названия треков могут отличаться на разных площадках

### Решение
- **Автоматическое распознавание** цензурированных версий по названию
- **Поиск оригиналов** на YouTube и SoundCloud
- **База известных пар** censored/uncensored для быстрого переключения
- **UI компонент** для переключения версий

---

## 🔧 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VersionSwitcher Component                            │   │
│  │  - Показывает статус (Clean/Explicit)                 │   │
│  │  - Кнопка "Найти без цензуры"                         │   │
│  │  - Переключатель версий                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  musicAPI.uncensored* методы                          │   │
│  │  - findUncensoredVersion()                            │   │
│  │  - getTrackCensorshipInfo()                           │   │
│  │  - addUncensoredPair()                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/uncensored/* endpoints                          │   │
│  │  - GET  /find      - Поиск uncensored версии          │   │
│  │  - POST /add-pair  - Добавление пары в базу           │   │
│  │  - GET  /check     - Проверка статуса цензуры         │   │
│  │  - GET  /playlist  - Массовый поиск для плейлиста     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  UncensoredFinderService                              │   │
│  │  - Распознавание по маркерам (clean, explicit, etc.)  │   │
│  │  - Поиск в локальной базе (uncensored_pairs.json)     │   │
│  │  - Поиск на YouTube (с таймаутом 10s)                 │   │
│  │  - Поиск на SoundCloud (с таймаутом 5s)               │   │
│  │  - Сохранение найденных пар                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### 1. Проверка статуса цензуры

**GET** `/api/uncensored/check`

**Параметры:**
- `track_id` (string): ID трека
- `title` (string): Название трека
- `artist` (string): Исполнитель

**Ответ:**
```json
{
  "track_id": "1",
  "title": "Bad Guy (Clean Version)",
  "artist": "Billie Eilish",
  "is_censored": true,
  "is_explicit": false,
  "clean_title": "Bad Guy",
  "has_uncensored_in_db": false
}
```

---

### 2. Поиск uncensored версии

**GET** `/api/uncensored/find`

**Параметры:**
- `track_id` (string): ID трека
- `title` (string): Название трека
- `artist` (string): Исполнитель
- `source` (string): Источник (youtube, soundcloud)

**Ответ (найдено):**
```json
{
  "status": "found",
  "source": "soundcloud",
  "confidence": 0.85,
  "track": {
    "id": "sc_12345",
    "title": "Bad Guy (Explicit Original)",
    "artist": "Billie Eilish",
    "duration": 194,
    "stream_url": "https://soundcloud.com/...",
    "cover": "https://...",
    "source": "soundcloud",
    "is_explicit": true
  },
  "search_query": "Billie Eilish Bad Guy explicit"
}
```

**Ответ (не найдено):**
```json
{
  "status": "not_found",
  "message": "Не удалось найти нецензурированную версию"
}
```

---

### 3. Добавление пары в базу

**POST** `/api/uncensored/add-pair`

**Body (JSON):**
```json
{
  "censored_title": "Bad Guy (Clean Version)",
  "uncensored_title": "Bad Guy (Explicit Original)",
  "artist": "Billie Eilish",
  "stream_url": "https://youtube.com/watch?v=...",
  "source": "youtube"
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "Добавлена пара: 'Bad Guy (Clean Version)' -> 'Bad Guy (Explicit Original)'"
}
```

---

### 4. Массовый поиск для плейлиста

**GET** `/api/uncensored/playlist`

**Параметры:**
- `track_ids` (string): Список ID через запятую
- `source` (string): Источник

**Ответ:**
```json
{
  "total_tracks": 10,
  "found_uncensored": 7,
  "results": {
    "track_id_1": {
      "source": "youtube",
      "confidence": 0.9,
      "uncensored_track": {...}
    },
    ...
  }
}
```

---

## 🎯 Стратегии поиска

### 1. Локальная база (быстро)
- Хранит известные пары censored/uncensored
- Поиск по хэшу "чистого" названия
- Fuzzy matching для похожих названий

### 2. YouTube (10s timeout)
- Поиск с запросом: `{artist} {clean_title} explicit original`
- Фильтрация по маркерам explicit в названии
- Автоматическое сохранение в базу

### 3. SoundCloud (5s timeout)
- Поиск с запросом: `{artist} {clean_title} original`
- Проверка на explicit версию
- Меньший приоритет чем YouTube

### 4. Mock fallback
- Если ничего не найдено, возвращается mock-данные
- Для демонстрации функционала

---

## 🏷️ Маркеры версий

### Censored (Clean) версии:
- `clean`
- `radio edit`
- `censored`
- `edited`
- `версия`
- `радио версия`
- `для эфира`

### Explicit (Original) версии:
- `explicit`
- `original`
- `uncensored`
- `dirty`
- `uncut`
- `оригинал`
- `нецензурная`
- `полная версия`
- `album version`
- `lp version`

---

## 💾 База данных пар

**Файл:** `backend/uncensored_pairs.json`

**Структура:**
```json
{
  "md5_hash_clean_title": {
    "clean_title": "Bad Guy",
    "uncensored_title": "Bad Guy (Explicit Original)",
    "artist": "Billie Eilish",
    "stream_url": "https://youtube.com/watch?v=...",
    "source": "youtube",
    "created_at": 123456.789
  },
  ...
}
```

**Пример:**
```bash
# После поиска пары сохраняются автоматически
cat backend/uncensored_pairs.json
```

---

## 🖥️ Frontend компонент

### VersionSwitcher

**Использование:**
```jsx
import VersionSwitcher from './components/VersionSwitcher';

function TrackPlayer({ track }) {
  const handleVersionChange = (data) => {
    if (data.type === 'uncensored_found') {
      console.log('Нашли explicit версию:', data.uncensored);
    } else if (data.type === 'switch_to_explicit') {
      // Переключить на explicit версию
      playTrack(data.uncensored);
    }
  };

  return (
    <div>
      <h3>{track.title}</h3>
      <VersionSwitcher
        track={track}
        onVersionChange={handleVersionChange}
      />
    </div>
  );
}
```

### Стили

- **Clean версия**: Серая метка "Clean"
- **Explicit версия**: Оранжевая метка "EXPLICIT"
- **Поиск**: Кнопка "Найти без цензуры" со спиннером
- **Переключатель**: Clean | Explicit (как toggle)

---

## 🧪 Тестирование

### Проверка цензуры:
```bash
curl "http://localhost:8081/api/uncensored/check?track_id=1&title=Bad+Guy+(Clean+Version)&artist=Billie+Eilish"
```

### Поиск uncensored:
```bash
curl "http://localhost:8081/api/uncensored/find?track_id=1&title=Bad+Guy+(Clean+Version)&artist=Billie+Eilish"
```

### Добавление пары:
```bash
curl -X POST "http://localhost:8081/api/uncensored/add-pair" \
  -H "Content-Type: application/json" \
  -d '{
    "censored_title": "Test (Clean)",
    "uncensored_title": "Test (Explicit)",
    "artist": "Test Artist",
    "stream_url": "https://youtube.com/test"
  }'
```

---

## 📊 Статистика

| Функция | Статус | Описание |
|---------|--------|----------|
| Проверка цензуры | ✅ | Распознавание по маркерам |
| Локальная база | ✅ | Хранение известных пар |
| Поиск YouTube | ✅ | С таймаутом 10s |
| Поиск SoundCloud | ✅ | С таймаутом 5s |
| UI компонент | ✅ | VersionSwitcher |
| Массовый поиск | ✅ | Для плейлистов |

---

## 🚀 Следующие улучшения

1. **Audio fingerprinting**
   - Сравнение аудио для точного matching
   - Интеграция с AcoustID или аналогами

2. **Crowdsourcing**
   - Пользователи добавляют пары
   - Голосование за правильные версии

3. **Автоматическое переключение**
   - При воспроизведении clean версии
   - Предложение переключиться на explicit

4. **Кэширование**
   - Redis для популярных запросов
   - TTL для устаревших данных

---

## 🔗 Связанные файлы

**Backend:**
- `backend/services/uncensored_finder_service.py` - Основной сервис
- `backend/routes_lite.py` - API endpoints (строка 757+)
- `backend/uncensored_pairs.json` - База пар (создаётся автоматически)

**Frontend:**
- `frontend/src/components/VersionSwitcher.jsx` - UI компонент
- `frontend/src/components/VersionSwitcher.module.css` - Стили
- `frontend/src/api/musicApi.js` - API методы (строка 543+)

---

**🎉 ТЕПЕРЬ МОЖНО НАХОДИТЬ ОРИГИНАЛЬНЫЕ ВЕРСИИ ТРЕКОВ БЕЗ ЦЕНЗУРЫ!**
