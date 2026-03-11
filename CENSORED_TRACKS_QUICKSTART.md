# 🚫 База цензурированных треков - Быстрый старт

## ✅ Что создано

### Бэкенд
- **models/censored_tracks.py** - Модели данных
- **services/censored_tracks_service.py** - Сервис SQLite БД
- **routes_censored_tracks.py** - API endpoints (9 штук)
- **auto_add_censored_tracks.py** - Авто-сканер логов
- **censored_tracks.db** - База данных (создаётся автоматически)

### Фронтенд
- **pages/CensoredTracks.jsx** - Страница управления
- **pages/CensoredTracks.module.css** - Стили
- **TabBar** - Добавлена вкладка "Цензура"

### Документация
- **CENSORED_TRACKS_DB.md** - Полная документация

---

## 🚀 Запуск

### 1. Запустить сервер

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### 2. Открыть страницу

```
http://localhost:5173/censored
```

Или через GitHub Pages:
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/censored
```

---

## 📡 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/censored-tracks/stats` | GET | Статистика базы |
| `/api/censored-tracks/search` | GET | Поиск треков |
| `/api/censored-tracks/{id}` | GET | Получить трек |
| `/api/censored-tracks/` | POST | Добавить трек |
| `/api/censored-tracks/{id}` | PUT | Обновить трек |
| `/api/censored-tracks/{id}` | DELETE | Удалить трек |
| `/api/censored-tracks/{id}/report` | POST | Пожаловаться |
| `/api/censored-tracks/{id}/replacement` | POST | Добавить замену |
| `/api/censored-tracks/export/json` | GET | Экспорт базы |
| `/api/censored-tracks/import/json` | POST | Импорт базы |

---

## 💡 Примеры использования

### Добавить трек через API

```bash
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lose Yourself",
    "artist": "Eminem",
    "platform_id": "abc123",
    "platform": "soundcloud",
    "censorship_type": "clean_version",
    "description": "Radio edit без ненормативной лексики"
  }'
```

### Получить статистику

```bash
curl "http://localhost:8000/api/censored-tracks/stats"
```

### Найти все непроверенные треки

```bash
curl "http://localhost:8000/api/censored-tracks/search?status=pending"
```

### Экспорт базы

```bash
curl "http://localhost:8000/api/censored-tracks/export/json" \
  -o censored_tracks.json
```

---

## 🤖 Авто-сканер

### Запустить сканирование логов

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python auto_add_censored_tracks.py
```

### Показать статистику

```bash
python auto_add_censored_tracks.py --stats
```

### Экспорт в JSON

```bash
python auto_add_censored_tracks.py --export-json backup.json
```

---

## 📊 Типы цензуры

| Тип | Описание |
|-----|----------|
| `blurred` | Звук заменён на beep |
| `muted` | Тишина вместо слов |
| `replaced` | Слово заменено |
| `deleted` | Трек удалён |
| `clean_version` | Clean/radio версия |

---

## 📈 Статусы

| Статус | Описание |
|--------|----------|
| `pending` | Ожидает проверки |
| `verified` | Проверен |
| `replaced` | Найдена замена |
| `false_positive` | Ложное срабатывание |

---

## 🧪 Тесты

```bash
# 1. Проверка сервиса
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -c "
from services.censored_tracks_service import censored_tracks_db
stats = censored_tracks_db.get_statistics()
print(f'Всего треков: {stats.total_censored}')
"

# 2. Проверка API
curl http://localhost:8000/api/censored-tracks/stats

# 3. Проверка фронтенда
# Открыть http://localhost:5173/censored
```

---

## 📁 Файлы

```
backend/
├── models/
│   ├── __init__.py
│   └── censored_tracks.py      # Модели
├── services/
│   └── censored_tracks_service.py  # Сервис БД
├── routes_censored_tracks.py   # API
├── auto_add_censored_tracks.py # Авто-сканер
└── censored_tracks.db          # SQLite база

frontend/
└── src/
    ├── pages/
    │   ├── CensoredTracks.jsx      # Страница
    │   └── CensoredTracks.module.css  # Стили
    └── components/
        └── TabBar.jsx              # Навигация

CENSORED_TRACKS_DB.md           # Документация
CENSORED_TRACKS_QUICKSTART.md   # Это файл
```

---

## 🎯 Сценарии

### 1. Ручное добавление
1. Открыть `/censored`
2. Нажать "+ Добавить трек"
3. Заполнить форму
4. Отправить

### 2. Поиск замены
1. Открыть трек
2. Нажать "🔍 Найти замену"
3. Система найдёт explicit версию

### 3. Массовый импорт
1. Экспортировать базу в JSON
2. Отредактировать
3. Импортировать обратно

---

## 🔧 Troubleshooting

### База не создаётся
```bash
ls -la /home/c1ten12/music-app/backend/censored_tracks.db
```

### API не отвечает
```bash
curl http://localhost:8000/api/censored-tracks/stats
```

### Фронтенд не работает
```bash
cd /home/c1ten12/music-app/frontend
npm run build
```

---

**🎵 Сохраняйте музыку без цензуры!**
