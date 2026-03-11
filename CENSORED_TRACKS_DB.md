# 🚫 База цензурированных треков - Документация

**Версия:** 1.0.0
**Дата:** 2026-03-10

---

## 📋 Описание

Локальная база данных для хранения информации о треках, которые подверглись цензуре:
- Заблюрены (beep вместо слов)
- Вырезаны (тишина вместо слов)
- Заменены (другие слова)
- Удалены из платформы
- Clean/radio версии

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (React)                           │
│  /censored - Страница управления базой                 │
│  - Просмотр треков                                      │
│  - Добавление/Редактирование                            │
│  - Поиск замен                                          │
│  - Экспорт/Импорт JSON                                  │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                          │
│  /api/censored-tracks/*                                 │
│  - routes_censored_tracks.py                            │
│  - services/censored_tracks_service.py                  │
│  - models/censored_tracks.py                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database                            │
│  backend/censored_tracks.db                             │
│  - Таблица: censored_tracks                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### Получить статистику

```http
GET /api/censored-tracks/stats
```

**Ответ:**
```json
{
  "total_censored": 42,
  "by_type": {
    "clean_version": 25,
    "blurred": 10,
    "deleted": 5,
    "muted": 2
  },
  "by_platform": {
    "soundcloud": 30,
    "youtube": 12
  },
  "by_status": {
    "pending": 15,
    "verified": 20,
    "replaced": 7
  },
  "replacements_found": 7,
  "verified_count": 20
}
```

---

### Поиск треков

```http
GET /api/censored-tracks/search?q=eminem&status=pending&limit=50
```

**Параметры:**
- `q` - Поисковый запрос
- `artist` - Фильтр по артисту
- `platform` - Фильтр по платформе
- `censorship_type` - Тип цензуры
- `status` - Статус (pending, verified, replaced, false_positive)
- `limit` - Лимит результатов
- `offset` - Смещение

---

### Получить трек по ID

```http
GET /api/censored-tracks/{track_id}
```

---

### Добавить трек

```http
POST /api/censored-tracks
Content-Type: application/json

{
  "title": "Bad Guy",
  "artist": "Billie Eilish",
  "platform_id": "123456",
  "platform": "soundcloud",
  "censorship_type": "clean_version",
  "description": "Clean version without explicit words",
  "censored_words": ["fuck", "shit"]
}
```

---

### Обновить трек

```http
PUT /api/censored-tracks/{track_id}
Content-Type: application/json

{
  "status": "verified",
  "replacement_found": true,
  "replacement_track_id": "789",
  "replacement_url": "https://youtube.com/watch?v=xxx",
  "replacement_platform": "youtube"
}
```

---

### Удалить трек

```http
DELETE /api/censored-tracks/{track_id}
```

---

### Сообщить о проблеме (увеличить счётчик жалоб)

```http
POST /api/censored-tracks/{track_id}/report
```

---

### Добавить замену

```http
POST /api/censored-tracks/{track_id}/replacement
Content-Type: application/json

{
  "replacement_track_id": "789",
  "replacement_url": "https://youtube.com/watch?v=xxx",
  "replacement_platform": "youtube"
}
```

---

### Экспорт в JSON

```http
GET /api/censored-tracks/export/json
```

---

### Импорт из JSON

```http
POST /api/censored-tracks/import/json
Content-Type: application/json

[ {...}, {...} ]
```

---

## 🖥️ Frontend

### Страница `/censored`

**Компонент:** `frontend/src/pages/CensoredTracks.jsx`

**Возможности:**
- ✅ Просмотр всех цензурированных треков
- ✅ Фильтрация по статусу
- ✅ Поиск по названию/артисту
- ✅ Добавление новых треков
- ✅ Проверка треков (verified/false_positive)
- ✅ Поиск замен через Anti-Censorship API
- ✅ Экспорт/Импорт JSON
- ✅ Статистика

**Доступ через TabBar:**
- Иконка: 🚫 Блок
- Название: "Цензура"

---

## 🤖 Автоматическое сканирование

### Скрипт `auto_add_censored_tracks.py`

**Использование:**

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Запуск сканирования
python auto_add_censored_tracks.py

# Показать статистику
python auto_add_censored_tracks.py --stats

# Экспорт в JSON
python auto_add_censored_tracks.py --export-json backup.json

# Импорт из JSON
python auto_add_censored_tracks.py --import-json backup.json
```

**Источники данных:**
1. Логи стриминга (`/tmp/music-app/streaming.log`)
2. Логи цензуры (`/tmp/music-app/censorship.log`)
3. JSON отчёты (`/tmp/music-app/censorship_reports.json`)

---

## 📊 Типы цензуры

| Тип | Описание | Пример |
|-----|----------|--------|
| `blurred` | Звук заменён на beep | beep вместо слова |
| `muted` | Звук вырезан (тишина) | пауза в треке |
| `replaced` | Слово заменено | другое слово |
| `deleted` | Трек удалён | "not available" |
| `clean_version` | Clean/radio версия | официальная чистая версия |

---

## 📈 Статусы треков

| Статус | Описание |
|--------|----------|
| `pending` | Ожидает проверки |
| `verified` | Проверен пользователем |
| `replaced` | Найдена замена |
| `false_positive` | Ложное срабатывание |

---

## 🔧 Настройка

### База данных

**Путь по умолчанию:**
```
/home/c1ten12/music-app/backend/censored_tracks.db
```

**Изменение пути:**
```python
from services.censored_tracks_service import CensoredTracksDatabase

db = CensoredTracksDatabase(db_path="/path/to/custom.db")
```

### Логи

**Путь по умолчанию:**
```
/tmp/music-app/
```

**Файлы:**
- `streaming.log` - Ошибки стриминга
- `censorship.log` - Логи Anti-Censorship
- `censorship_reports.json` - JSON отчёты

---

## 📝 Примеры использования

### 1. Добавление трека через API

```bash
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lose Yourself",
    "artist": "Eminem",
    "platform_id": "abc123",
    "platform": "soundcloud",
    "censorship_type": "clean_version",
    "description": "Radio edit without explicit lyrics"
  }'
```

### 2. Поиск всех непроверенных треков

```bash
curl "http://localhost:8000/api/censored-tracks/search?status=pending"
```

### 3. Поиск замены для трека

```bash
# Из фронтенда автоматически ищет через:
# /api/censorship/search-uncensored?q={title}+{artist}+explicit
```

### 4. Экспорт базы

```bash
curl "http://localhost:8000/api/censored-tracks/export/json" \
  -o censored_tracks_backup.json
```

---

## 🧪 Тестирование

### Проверка работы API

```bash
# 1. Запустить сервер
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000

# 2. Проверить статистику
curl http://localhost:8000/api/censored-tracks/stats

# 3. Добавить тестовый трек
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Track",
    "artist": "Test Artist",
    "platform_id": "test123",
    "platform": "soundcloud",
    "censorship_type": "clean_version"
  }'

# 4. Проверить поиск
curl "http://localhost:8000/api/censored-tracks/search?q=Test"
```

### Проверка фронтенда

1. Откройте браузер
2. Перейдите на `/censored`
3. Проверьте:
   - Отображение статистики
   - Список треков
   - Фильтрацию
   - Форму добавления
   - Кнопки действий

---

## 📦 Структура файлов

```
backend/
├── models/
│   └── censored_tracks.py       # Модели данных
├── services/
│   └── censored_tracks_service.py  # Сервис БД
├── routes_censored_tracks.py    # API endpoints
├── auto_add_censored_tracks.py  # Авто-сканер
└── censored_tracks.db           # SQLite база

frontend/
├── src/
│   ├── pages/
│   │   ├── CensoredTracks.jsx     # Страница
│   │   └── CensoredTracks.module.css  # Стили
│   ├── components/
│   │   └── TabBar.jsx             # Навигация
│   └── App.jsx                    # Роутинг
└── ...

docs/
└── CENSORED_TRACKS_DB.md        # Эта документация
```

---

## 🎯 Сценарии использования

### Сценарий 1: Ручное добавление

1. Пользователь обнаруживает цензурный трек
2. Открывает `/censored`
3. Нажимает "+ Добавить трек"
4. Заполняет форму
5. Отправляет

### Сценарий 2: Автоматическое обнаружение

1. Скрипт сканирует логи
2. Находит ошибки воспроизведения
3. Добавляет треки в базу
4. Пользователь проверяет в интерфейсе

### Сценарий 3: Поиск замены

1. Пользователь видит трек со статусом "pending"
2. Нажимает "🔍 Найти замену"
3. Система ищет через Anti-Censorship API
4. Находит explicit версию
5. Сохраняет как замену

### Сценарий 4: Массовый импорт

1. Администратор экспортирует базу
2. Редактирует JSON
3. Импортирует обратно
4. Получает обновлённую базу

---

## 🔒 Безопасность

- **SQLite** - локальная база, нет сетевого доступа
- **Валидация** - все входные данные проверяются
- **Уникальность** - дубликаты треков отклоняются

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| Макс. треков | Неограниченно |
| Размер БД | ~100 KB на 1000 треков |
| Скорость поиска | <50 ms |
| Поддержка | Python 3.9+ |

---

## 🐛 Troubleshooting

### База не создаётся

```bash
# Проверка прав доступа
ls -la /home/c1ten12/music-app/backend/

# Проверка импортов
python -c "from services.censored_tracks_service import censored_tracks_db"
```

### API не отвечает

```bash
# Проверка логов
tail -f /tmp/music-app/backend.log

# Проверка роутов
curl http://localhost:8000/docs
```

### Фронтенд не загружается

```bash
# Пересборка
cd /home/c1ten12/music-app/frontend
npm run build
```

---

## 📝 Changelog

### v1.0.0 (2026-03-10)
- ✅ SQLite база данных
- ✅ 9 API endpoints
- ✅ Frontend интерфейс
- ✅ Авто-сканер логов
- ✅ Экспорт/Импорт JSON
- ✅ Поиск замен

---

**🎵 Сохраняйте музыку без цензуры!**
