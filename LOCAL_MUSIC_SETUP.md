# 🎵 ПОЛНАЯ ИНСТРУКЦИЯ: Локальная музыкальная база без цензуры

**Версия:** 1.0
**Дата:** 2026-03-10

---

## 📋 ЧТО У ВАС БУДЕТ

1. **Локальная база данных** цензурированных треков (SQLite)
2. **Библиотека uncensored версий** (MP3 файлы)
3. **Музыкальный сервер** с REST API
4. **Веб-интерфейс** для поиска и воспроизведения
5. **Автоматическое скачивание** оригинальных версий

---

## 🏗️ АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────┐
│              Веб-интерфейс (Frontend)                   │
│  http://localhost:5173/censored                        │
│  - Просмотр цензурированных треков                      │
│  - Поиск замен                                          │
│  - Управление базой                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Backend API (FastAPI, порт 8000)                │
│  /api/censored-tracks/*                                 │
│  - База цензурированных треков (SQLite)                 │
│  - Поиск uncensored версий                              │
│  - Anti-Censorship система                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Скрипты скачивания (download_*.py)                   │
│  - YouTube через yt-dlp                                 │
│  - Telegram боты                                        │
│  - SoundCloud API                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Локальный музыкальный сервер                    │
│  local_music_server.py (порт 8080)                      │
│  - База скачанных треков                                │
│  - REST API для воспроизведения                         │
│  - Subsonic API (совместимость)                         │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         music_library/                                   │
│  ├── Artist_1/                                          │
│  │   ├── Track_1.mp3                                    │
│  │   └── Track_2.mp3                                    │
│  ├── Artist_2/                                          │
│  │   └── ...                                            │
│  └── uncensored_playlist.m3u                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 УСТАНОВКА

### Шаг 1: Установка зависимостей

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Основные зависимости
pip install fastapi uvicorn yt-dlp telethon mutagen

# Дополнительные (опционально)
pip install psycopg2-binary  # Для OMDB
```

### Шаг 2: Установка ffmpeg (для конвертации в MP3)

```bash
sudo apt update
sudo apt install ffmpeg
```

### Шаг 3: Проверка установки

```bash
python -c "import yt_dlp, telethon, mutagen; print('✅ Все зависимости установлены')"
```

---

## 📥 СКАЧИВАНИЕ UNCENSORED ВЕРСИЙ

### Способ 1: Из базы цензурированных треков

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Скачивание 20 треков со статусом "pending"
python download_uncensored_massive.py --from-db --status pending --limit 20 --explicit

# Все непроверенные треки
python download_uncensored_massive.py --from-db --status all --limit 100 --explicit
```

**Что делает скрипт:**
1. Берёт треки из базы `censored_tracks.db`
2. Ищет explicit версии на YouTube
3. Скачивает в `music_library/{Artist}/{Track}.mp3`
4. Создаёт плейлист `uncensored_playlist.m3u`
5. Экспортирует библиотеку в `library.json`

### Способ 2: Из JSON файла

```bash
# Создайте список треков
cat > my_tracks.json << 'EOF'
[
  {"artist": "Eminem", "title": "Lose Yourself", "url": ""},
  {"artist": "Billie Eilish", "title": "Bad Guy", "url": ""},
  {"artist": "The Weeknd", "title": "Blinding Lights", "url": ""}
]
EOF

# Скачивание
python download_uncensored_massive.py --input my_tracks.json --output music_library --explicit
```

### Способ 3: Через Telegram ботов

```bash
# Отредактируйте telegram_auto_download.py
nano telegram_auto_download.py

# Добавьте свои треки в список TRACKS
TRACKS = [
    "Eminem Lose Yourself explicit",
    "50 Cent In Da Club uncensored",
    # ...
]

# Запуск
python telegram_auto_download.py
```

---

## 🎵 ЗАПУСК МУЗЫКАЛЬНОГО СЕРВЕРА

### Шаг 1: Запуск сервера

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Запуск локального музыкального сервера
python local_music_server.py --port 8080 --music-dir music_library --scan
```

**Параметры:**
- `--port 8080` - Порт сервера
- `--music-dir music_library` - Папка с музыкой
- `--scan` - Сканировать папку при запуске
- `--db local_music.db` - Файл базы данных

### Шаг 2: Проверка работы

```bash
# Статистика библиотеки
curl http://localhost:8080/api/stats

# Все треки
curl http://localhost:8080/api/tracks?limit=50

# Поиск
curl "http://localhost:8080/api/search?q=Eminem&limit=10"

# Случайные треки
curl "http://localhost:8080/api/random?limit=20"
```

### Шаг 3: Воспроизведение

**Прямая ссылка на трек:**
```
http://localhost:8080/music/Artist_Name/Track_Name.mp3
```

**В VLC:**
```
vlc http://localhost:8080/api/tracks/1/stream
```

---

## 🖥️ ВЕБ-ИНТЕРФЕЙС

### Доступ к интерфейсу

**Frontend (управление базой цензурированных треков):**
```
http://localhost:5173/censored
```

**API Docs (Swagger):**
```
http://localhost:8000/docs
```

**Музыкальный сервер:**
```
http://localhost:8080
```

### Управление через веб-интерфейс

1. **Просмотр базы цензурированных треков**
   - Откройте `/censored`
   - Фильтруйте по статусу
   - Ищите по названию/артисту

2. **Поиск замены**
   - Кликните на трек
   - Нажмите "🔍 Найти замену"
   - Система найдёт explicit версию

3. **Скачивание**
   ```bash
   python download_uncensored_massive.py --from-db --limit 10
   ```

4. **Прослушивание**
   - Откройте `http://localhost:8080`
   - Ищите по артисту/названию
   - Воспроизводите напрямую

---

## 📊 УПРАВЛЕНИЕ БИБЛИОТЕКОЙ

### Просмотр статистики

```bash
curl http://localhost:8080/api/stats
```

**Пример ответа:**
```json
{
  "tracks": 150,
  "artists": 45,
  "albums": 30,
  "total_size_gb": 2.5,
  "total_plays": 500
}
```

### Добавление новых треков

**Автоматическое сканирование:**
```bash
# При запуске сервера
python local_music_server.py --scan

# Или через API
curl "http://localhost:8080/api/scan?directory=/path/to/music"
```

**Вручную через базу:**
```bash
python -c "
from local_music_server import LocalMusicDatabase
db = LocalMusicDatabase()
db.scan_directory('music_library')
"
```

### Экспорт библиотеки

```bash
# JSON экспорт
cat music_library/library.json

# M3U плейлист
cat music_library/uncensored_playlist.m3u
```

---

## 🔄 ПОЛНЫЙ РАБОЧИЙ ПРОЦЕСС

### 1. Обнаружение цензурного трека

```bash
# Вы заметили что трек цензурирован
# Например: "Lose Yourself" - Eminem (заблюрены слова)
```

### 2. Добавление в базу цензурированных треков

```bash
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lose Yourself",
    "artist": "Eminem",
    "platform_id": "yt_abc123",
    "platform": "youtube",
    "censorship_type": "blurred",
    "description": "Заблюрены слова на 1:15 и 2:30"
  }'
```

### 3. Поиск uncensored версии

```bash
# Через веб-интерфейс: кнопка "🔍 Найти замену"

# Или через API:
curl "http://localhost:8000/api/censorship/search-uncensored?q=Eminem%20Lose%20Yourself&limit=5"
```

### 4. Скачивание

```bash
# Автоматически из базы
python download_uncensored_massive.py --from-db --status pending --limit 5

# Конкретный трек
python download_uncensored_massive.py --input track.json
```

### 5. Добавление в музыкальный сервер

```bash
# Сканирование папки
curl "http://localhost:8080/api/scan?directory=music_library"

# Или перезапуск сервера с --scan
python local_music_server.py --port 8080 --scan
```

### 6. Воспроизведение

```bash
# Прямая ссылка
vlc "http://localhost:8080/music/Eminem/Lose_Yourself_Uncensored.mp3"

# Через API
curl "http://localhost:8080/api/tracks/1/stream"
```

### 7. Обновление статуса в базе

```bash
curl -X POST "http://localhost:8000/api/censored-tracks/1/replacement" \
  -H "Content-Type: application/json" \
  -d '{
    "replacement_track_id": "local_1",
    "replacement_url": "http://localhost:8080/music/Eminem/Lose_Yourself.mp3",
    "replacement_platform": "local"
  }'
```

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
/home/c1ten12/music-app/
├── backend/
│   ├── censored_tracks.db              # База цензурированных треков
│   ├── local_music.db                  # База музыкального сервера
│   │
│   ├── download_uncensored_massive.py  # Скрипт скачивания
│   ├── local_music_server.py           # Музыкальный сервер
│   ├── telegram_auto_download.py       # Telegram загрузчик
│   │
│   ├── services/
│   │   ├── censored_tracks_service.py  # Сервис базы
│   │   └── ...
│   │
│   └── music_library/                  # Скачанная музыка
│       ├── Eminem/
│       │   └── Lose Yourself (Uncensored).mp3
│       ├── Billie Eilish/
│       │   └── Bad Guy (Explicit).mp3
│       ├── uncensored_playlist.m3u
│       └── library.json
│
├── frontend/
│   └── src/
│       └── pages/
│           └── CensoredTracks.jsx      # Веб-интерфейс
│
├── QUICKSTART_CENSORED.md              # Быстрый старт
├── INSTRUCTION_CENSORED_TRACKS.md      # Полная инструкция
└── LOCAL_MUSIC_SETUP.md                # Этот файл
```

---

## 🎯 ГОТОВЫЕ КОМАНДЫ

### Быстрый старт

```bash
# 1. Запуск API цензурированных треков
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 &

# 2. Скачивание 10 uncensored треков
python download_uncensored_massive.py --from-db --limit 10 --explicit

# 3. Запуск музыкального сервера
python local_music_server.py --port 8080 --scan
```

### Массовое скачивание

```bash
# Скачать все непроверенные треки
python download_uncensored_massive.py --from-db --status all --limit 100 --explicit

# Скачать из JSON списка
python download_uncensored_massive.py --input tracks.json --explicit

# Скачать конкретного артиста
python -c "
import json
tracks = [{'artist': 'Eminem', 'title': t, 'url': ''} for t in [
    'Lose Yourself', 'Without Me', 'The Real Slim Shady'
]]
with open('eminem.json', 'w') as f:
    json.dump(tracks, f)
"
python download_uncensored_massive.py --input eminem.json --explicit
```

### Управление библиотекой

```bash
# Статистика
curl http://localhost:8080/api/stats | python3 -m json.tool

# Все треки
curl http://localhost:8080/api/tracks?limit=100 | python3 -m json.tool

# Поиск артиста
curl "http://localhost:8080/api/search?q=Eminem&limit=20" | python3 -m json.tool

# Случайные треки для вечеринки
curl "http://localhost:8080/api/random?limit=50" | python3 -m json.tool
```

### Резервное копирование

```bash
# База цензурированных треков
python auto_add_censored_tracks.py --export-json backup_censored_$(date +%Y%m%d).json

# Музыкальная библиотека
cp local_music.db backup_music_$(date +%Y%m%d).db

# Скачанная музыка
tar -czf music_library_$(date +%Y%m%d).tar.gz music_library/
```

---

## 🔧 НАСТРОЙКА PROXY (для обхода блокировок)

Если YouTube заблокирован:

```bash
# В .env добавьте
PROXY_URL=http://proxy-server:port

# Или в скрипте скачивания
ydl_opts = {
    'proxy': 'http://proxy-server:port',
    # ...
}
```

---

## ❓ ЧАСТЫЕ ВОПРОСЫ

### Q: Сколько места нужно для библиотеки?
**A:** 
- 1 трек ≈ 5-10 MB (MP3 320kbps)
- 100 треков ≈ 500 MB - 1 GB
- 1000 треков ≈ 5-10 GB

### Q: Как обновлять библиотеку?
**A:** 
```bash
# Пересканировать папку
curl "http://localhost:8080/api/scan?directory=music_library"
```

### Q: Можно ли слушать с телефона?
**A:** Да, если сервер доступен в сети:
```
http://YOUR_SERVER_IP:8080/music/Artist/Track.mp3
```

### Q: Как экспортировать для другого плеера?
**A:** 
```bash
# M3U плейлист
cat music_library/uncensored_playlist.m3u

# JSON библиотека
cat music_library/library.json
```

### Q: Что если трек не находится?
**A:** 
1. Попробуйте другое название
2. Добавьте "explicit" к запросу
3. Используйте Telegram ботов

---

## 🎵 ИНТЕГРАЦИЯ С ДРУГИМИ СЕРВИСАМИ

### Subsonic API (совместимость)

```bash
# Сервер поддерживает Subsonic API
# Подключите через:
# - DSub (Android)
# - Substreamer (iOS)
# - Sonos

URL: http://YOUR_SERVER_IP:8080/rest
Username: admin
Password: admin
```

### Plex / Jellyfin

```bash
# Добавьте папку music_library как медиатеку
# Тип: Music
# Путь: /home/c1ten12/music-app/backend/music_library
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация
- `QUICKSTART_CENSORED.md` — Быстрый старт (5 шагов)
- `INSTRUCTION_CENSORED_TRACKS.md` — Полная инструкция
- `CENSORED_TRACKS_DB.md` — Документация API

### Скрипты
- `download_uncensored_massive.py` — Массовое скачивание
- `local_music_server.py` — Музыкальный сервер
- `telegram_auto_download.py` — Telegram загрузчик
- `auto_add_censored_tracks.py` — Авто-сканер логов

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **Наполните библиотеку:**
   ```bash
   python download_uncensored_massive.py --from-db --limit 50
   ```

2. **Запустите сервер:**
   ```bash
   python local_music_server.py --port 8080 --scan
   ```

3. **Откройте веб-интерфейс:**
   ```
   http://localhost:8080
   ```

4. **Наслаждайтесь музыкой без цензуры!**

---

**🎵 ПРИЯТНОГО ПРОСЛУШИВАНИЯ!**
