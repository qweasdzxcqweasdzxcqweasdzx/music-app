# 🚀 БЫСТРЫЙ СТАРТ: База цензурированных треков

## 📋 ЧТО У ВАС ЕСТЬ

| Файл | Назначение |
|------|------------|
| `services/censored_tracks.db` | База данных (4 трека) |
| `censored_tracks_export.json` | Экспорт базы |
| `download_from_censored_db.py` | Скрипт скачивания uncensored версий |
| `INSTRUCTION_CENSORED_TRACKS.md` | Полная инструкция |

---

## ⚡ 5 ШАГОВ ДЛЯ НАЧАЛА РАБОТЫ

### Шаг 1: Проверка базы

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Посмотреть статистику
python auto_add_censored_tracks.py --stats
```

**Ожидаемый результат:**
```
📊 Статистика:
   Всего: 4
   По типам: clean_version: 2, blurred: 1, muted: 1
```

---

### Шаг 2: Запуск сервера

```bash
# В одном окне терминала
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

**Проверка:**
```bash
# В другом окне
curl http://localhost:8000/api/censored-tracks/stats
```

---

### Шаг 3: Просмотр базы

**Откройте в браузере:**
```
http://localhost:5173/censored
```

**Или GitHub Pages:**
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/censored
```

---

### Шаг 4: Поиск и скачивание замены

```bash
# Запуск скрипта скачивания
python download_from_censored_db.py --status pending --limit 5
```

**Скрипт:**
1. Берёт треки со статусом "pending"
2. Ищет uncensored версии через API
3. Предлагает добавить замену в базу
4. Скачивает найденные треки
5. Создаёт плейлист

---

### Шаг 5: Просмотр результата

```bash
# Посмотреть скачанные треки
ls -lh downloaded_uncensored/

# Плейлист
cat downloaded_uncensored/uncensored_playlist.m3u
```

---

## 📥 ЭКСПОРТ БАЗЫ

```bash
# Экспорт в JSON
python auto_add_censored_tracks.py --export-json backup.json

# Файл появится: backup.json
```

---

## 🎯 ПОЛНЫЙ РАБОЧИЙ ПРОЦЕСС

```
1. Обнаружение цензурного трека
   ↓
2. Добавление в базу (веб или API)
   ↓
3. Поиск замены (кнопка "🔍 Найти замену")
   ↓
4. Скачивание (скрипт download_from_censored_db.py)
   ↓
5. Проверка статуса (веб-интерфейс)
```

---

## 🔧 КОМАНДЫ

### Управление базой

```bash
# Статистика
python auto_add_censored_tracks.py --stats

# Поиск треков
curl "http://localhost:8000/api/censored-tracks/search?status=pending"

# Добавить трек
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{"title":"Трек","artist":"Артист","platform_id":"123","platform":"youtube","censorship_type":"blurred"}'

# Экспорт
python auto_add_censored_tracks.py --export-json backup.json

# Импорт
python auto_add_censored_tracks.py --import-json backup.json
```

### Скачивание

```bash
# Через yt-dlp (YouTube, SoundCloud)
python download_from_censored_db.py --method ytdlp --limit 10

# Через Telegram ботов
python download_from_censored_db.py --method telegram --limit 10

# Все треки
python download_from_censored_db.py --status all
```

---

## 📊 СТАТУСЫ ТРЕКОВ

| Статус | Описание | Что делать |
|--------|----------|------------|
| `pending` | Ожидает проверки | Проверить, найти замену |
| `verified` | Проверен | Можно скачать замену |
| `replaced` | Найдена замена | Скачать и заменить |
| `false_positive` | Ошибка | Удалить из базы |

---

## 🎵 ТИПЫ ЦЕНЗУРЫ

| Тип | Описание | Пример |
|-----|----------|--------|
| `blurred` | Заблюрено (beep) | beep вместо слова |
| `muted` | Тишина | Вырезана часть |
| `replaced` | Замена слова | Другое слово |
| `deleted` | Удалён | "not available" |
| `clean_version` | Radio версия | Официально чистая |

---

## ❓ ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Сервер не запускается
```bash
# Проверка порта
ss -tlnp | grep 8000

# Убить старый процесс
pkill -f uvicorn

# Запустить снова
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000
```

### База не создаётся
```bash
# Проверка прав
ls -la services/

# Удалить и создать заново
rm services/censored_tracks.db
python -c "from services.censored_tracks_service import censored_tracks_db; print('OK')"
```

### Фронтенд не работает
```bash
cd /home/c1ten12/music-app/frontend
npm run build
```

---

## 📚 ДОКУМЕНТАЦИЯ

- `INSTRUCTION_CENSORED_TRACKS.md` — Полная инструкция
- `CENSORED_TRACKS_DB.md` — Документация API
- `CENSORED_TRACKS_QUICKSTART.md` — Краткий гид

---

**🎵 ПРИЯТНОГО ПОЛЬЗОВАНИЯ!**
