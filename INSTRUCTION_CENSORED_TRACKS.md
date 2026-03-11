# 🎵 Полная инструкция: Работа с базой цензурированных треков

**Версия:** 1.0
**Дата:** 2026-03-10

---

## 📋 Содержание

1. [Что такое база цензурированных треков](#что-такое-база-цензурированных-треков)
2. [Установка и настройка](#установка-и-настройка)
3. [Запуск сервера](#запуск-сервера)
4. [Просмотр базы через веб-интерфейс](#просмотр-базы-через-веб-интерфейс)
5. [Добавление треков в базу](#добавление-треков-в-базу)
6. [Поиск и скачивание оригинальных версий](#поиск-и-скачивание-оригинальных-версий)
7. [Экспорт и импорт базы](#экспорт-и-импорт-базы)
8. [Автоматическое скачивание через Telegram](#автоматическое-скачивание-через-telegram)

---

## 📖 Что такое база цензурированных треков

Это локальная база данных (SQLite) которая хранит информацию о треках, подвергшихся цензуре:

| Тип цензуры | Описание |
|-------------|----------|
| 🔇 **Blurred** | Слова заменены на beep |
| 🔇 **Muted** | Вырезана часть (тишина) |
| 🔄 **Replaced** | Слова заменены на другие |
| ❌ **Deleted** | Трек удалён из платформы |
| 📻 **Clean Version** | Официальная radio версия |

**Пример:**
- Трек: "Lose Yourself" - Eminem
- Проблема: Заблюрены 2 слова (censorship_type: blurred)
- Решение: Найти и скачать оригинальную explicit версию

---

## 🛠️ Установка и настройка

### Шаг 1: Проверка зависимостей

```bash
# Перейдите в директорию backend
cd /home/c1ten12/music-app/backend

# Проверьте что виртуальное окружение есть
ls -la venv/

# Активируйте его
source venv/bin/activate

# Проверьте установленные пакеты
pip list | grep -E "telethon|yt-dlp|fastapi"
```

**Должно быть установлено:**
- ✅ telethon (для Telegram)
- ✅ yt-dlp (для YouTube/SoundCloud)
- ✅ fastapi (для API)

### Шаг 2: Проверка базы данных

```bash
# Проверьте что база существует
ls -lh services/censored_tracks.db

# Посмотрите статистику
python auto_add_censored_tracks.py --stats
```

**Пример вывода:**
```
📊 Статистика базы цензурированных треков:
   Всего: 4
   По типам: {'clean_version': 2, 'blurred': 1, 'muted': 1}
   По платформам: {'soundcloud': 3, 'youtube': 1}
   По статусам: {'pending': 4}
   Найдено замен: 0
   Проверено: 0
```

---

## 🚀 Запуск сервера

### Шаг 1: Запуск Backend API

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Запуск сервера
python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка работы:**

Откройте новое окно терминала:

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Проверка API цензурированных треков
curl http://localhost:8000/api/censored-tracks/stats
```

**Успешный ответ:**
```json
{
  "total_censored": 4,
  "by_type": {"clean_version": 2, "blurred": 1, "muted": 1},
  "by_platform": {"soundcloud": 3, "youtube": 1},
  ...
}
```

### Шаг 2: Запуск Frontend (опционально)

```bash
cd /home/c1ten12/music-app/frontend

# Запуск dev сервера
npm run dev

# Или сборка для продакшена
npm run build
```

---

## 🖥️ Просмотр базы через веб-интерфейс

### Шаг 1: Откройте браузер

Перейдите по адресу:
```
http://localhost:5173/censored
```

Или если используете GitHub Pages:
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/censored
```

### Шаг 2: Интерфейс

**Вы увидите:**

1. **Статистика сверху:**
   - Всего треков
   - Проверено
   - Найдено замен
   - Ожидают проверки

2. **Кнопки фильтров:**
   - Все
   - Ожидают (pending)
   - Проверено (verified)
   - С заменой (replaced)

3. **Список треков:**
   - Название и артист
   - Тип цензуры (цветной бейдж)
   - Статус
   - Платформа

4. **Действия с треком** (кликните на трек):
   - ✓ Проверить
   - Ложное срабатывание
   - 🔍 Найти замену
   - 🗑️ Удалить

---

## ➕ Добавление треков в базу

### Способ 1: Через веб-интерфейс

1. Откройте `/censored`
2. Нажмите **"+ Добавить трек"**
3. Заполните форму:
   - Название трека
   - Исполнитель
   - ID на платформе (например, из URL)
   - Платформа (SoundCloud, YouTube, VK)
   - Тип цензуры
   - Описание проблемы
4. Нажмите **"Добавить"**

### Способ 2: Через API

```bash
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Название трека",
    "artist": "Исполнитель",
    "platform_id": "id_из_url",
    "platform": "youtube",
    "censorship_type": "blurred",
    "description": "Заблюрено слово на 1:23"
  }'
```

### Способ 3: Автоматическое сканирование логов

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Сканирование и добавление из логов
python auto_add_censored_tracks.py
```

---

## 🔍 Поиск и скачивание оригинальных версий

### Шаг 1: Поиск замены через API

```bash
# Для конкретного трека
curl "http://localhost:8000/api/censorship/search-uncensored?q=Eminem%20Lose%20Yourself&limit=5"
```

### Шаг 2: Добавление найденной замены

```bash
curl -X POST "http://localhost:8000/api/censored-tracks/1/replacement" \
  -H "Content-Type: application/json" \
  -d '{
    "replacement_track_id": "new_track_id",
    "replacement_url": "https://youtube.com/watch?v=xxx",
    "replacement_platform": "youtube"
  }'
```

### Шаг 3: Скачивание оригинальной версии

**Вариант A: Через yt-dlp (YouTube/SoundCloud)**

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Скачивание одного трека
python -c "
import yt_dlp
url = 'https://www.youtube.com/watch?v=SwC51gO5ZrQ'  # Замените на свой URL
ydl_opts = {
    'format': 'bestaudio[ext=mp3]/bestaudio/best',
    'outtmpl': 'downloaded_tracks/%(artist)s - %(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
"
```

**Вариант B: Через Telegram бота**

Смотрите раздел [Автоматическое скачивание через Telegram](#автоматическое-скачивание-через-telegram)

---

## 💾 Экспорт и импорт базы

### Экспорт в JSON

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Через скрипт
python auto_add_censored_tracks.py --export-json backup_$(date +%Y%m%d).json

# Через API (если сервер запущен)
curl http://localhost:8000/api/censored-tracks/export/json -o censored_tracks.json
```

**Файл появится:**
- `backup_20260310.json` — резервная копия
- `censored_tracks.json` — текущий экспорт

### Импорт из JSON

```bash
# Через скрипт
python auto_add_censored_tracks.py --import-json backup_20260310.json

# Через API
curl -X POST "http://localhost:8000/api/censored-tracks/import/json" \
  -H "Content-Type: application/json" \
  -d @backup_20260310.json
```

### Резервное копирование SQLite базы

```bash
# Копирование файла базы
cp services/censored_tracks.db services/censored_tracks_backup_$(date +%Y%m%d).db

# Восстановление из копии
cp services/censored_tracks_backup_20260310.db services/censored_tracks.db
```

---

## 🤖 Автоматическое скачивание через Telegram

### Шаг 1: Настройка скрипта

Откройте файл `telegram_auto_download.py`:

```bash
nano telegram_auto_download.py
```

**Отредактируйте список треков:**

```python
TRACKS = [
    "Eminem Lose Yourself explicit",
    "Billie Eilish Bad Guy original",
    # Добавьте свои треки
]
```

### Шаг 2: Запуск скачивания

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Запуск скрипта
python telegram_auto_download.py
```

### Шаг 3: Авторизация в Telegram

1. Скрипт запросит номер телефона
2. Введите номер в формате `+79991234567`
3. Получите код подтверждения в Telegram
4. Введите код в терминал

### Шаг 4: Проверка результата

```bash
# Посмотреть скачанные файлы
ls -lh static/tracks/

# Количество файлов
ls static/tracks/*.mp3 | wc -l
```

---

## 📝 Полный рабочий процесс

### Пример: Обработка цензурного трека

**1. Обнаружение проблемы:**
```bash
# Вы заметили что трек цензурирован
# Например: "Lose Yourself" - Eminem (заблюрены слова)
```

**2. Добавление в базу:**
```bash
curl -X POST "http://localhost:8000/api/censored-tracks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lose Yourself",
    "artist": "Eminem",
    "platform_id": "ly456",
    "platform": "soundcloud",
    "censorship_type": "blurred",
    "description": "Заблюрены слова на 1:15 и 2:30"
  }'
```

**3. Поиск замены:**
```bash
# Через веб-интерфейс нажмите "🔍 Найти замену"
# Или через API:
curl "http://localhost:8000/api/censorship/search-uncensored?q=Eminem%20Lose%20Yourself%20explicit&limit=5"
```

**4. Скачивание оригинала:**
```bash
# Создайте файл download_uncensored.py
nano download_uncensored.py
```

**Содержимое:**
```python
#!/usr/bin/env python3
import yt_dlp
import os

os.makedirs('downloaded_tracks', exist_ok=True)

url = 'https://www.youtube.com/watch?v=SwC51gO5ZrQ'  # Найденный URL
ydl_opts = {
    'format': 'bestaudio[ext=mp3]/bestaudio/best',
    'outtmpl': 'downloaded_tracks/Eminem_-_Lose_Yourself_Explicit.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("✅ Трек скачан!")
```

**Запуск:**
```bash
source venv/bin/activate
python download_uncensored.py
```

**5. Добавление замены в базу:**
```bash
curl -X POST "http://localhost:8000/api/censored-tracks/3/replacement" \
  -H "Content-Type: application/json" \
  -d '{
    "replacement_track_id": "yt_abc123",
    "replacement_url": "https://www.youtube.com/watch?v=SwC51gO5ZrQ",
    "replacement_platform": "youtube"
  }'
```

**6. Проверка статуса:**
```bash
curl "http://localhost:8000/api/censored-tracks/3"
```

---

## 🧰 Полезные команды

### Проверка статуса

```bash
# Статистика базы
python auto_add_censored_tracks.py --stats

# Просмотр всех треков
curl "http://localhost:8000/api/censored-tracks/search?limit=100" | python3 -m json.tool

# Только непроверенные
curl "http://localhost:8000/api/censored-tracks/search?status=pending" | python3 -m json.tool
```

### Массовые операции

```bash
# Удалить все false_positive
curl "http://localhost:8000/api/censored-tracks/search?status=false_positive" | \
  python3 -c "import sys, json; [print(f'curl -X DELETE http://localhost:8000/api/censored-tracks/{t[\"id\"]}') for t in json.load(sys.stdin)]" | bash

# Экспорт всех verified
curl "http://localhost:8000/api/censored-tracks/search?status=verified" -o verified_tracks.json
```

### Обслуживание

```bash
# Очистка кэша
rm -rf __pycache__/
find . -name "*.pyc" -delete

# Проверка целостности БД
sqlite3 services/censored_tracks.db "PRAGMA integrity_check;"

# Резервное копирование
cp services/censored_tracks.db backup_$(date +%Y%m%d_%H%M%S).db
```

---

## ❓ Частые вопросы

### Q: Где хранится база?
**A:** `/home/c1ten12/music-app/backend/services/censored_tracks.db`

### Q: Как перенести базу на другой сервер?
**A:** Скопируйте файл `censored_tracks.db` и JSON экспорт

### Q: Можно ли использовать MongoDB вместо SQLite?
**A:** Да, измените `services/censored_tracks_service.py` для работы с MongoDB

### Q: Как добавить своего Telegram бота?
**A:** Добавьте имя бота в список `BOTS` в `telegram_auto_download.py`

### Q: Что делать если скрипт Telegram не работает?
**A:** 
1. Проверьте API ключи (API_ID, API_HASH)
2. Убедитесь что номер телефона верный
3. Проверьте что боты активны (@vk_music_bot, @SaveMusicBot)

---

## 📞 Поддержка

**Документация:**
- `CENSORED_TRACKS_DB.md` — Полная документация
- `CENSORED_TRACKS_QUICKSTART.md` — Быстрый старт

**Логи:**
- `/tmp/music-app/backend.log` — Логи сервера
- `/tmp/cf.log` — Логи Cloudflare

**API Docs:**
- http://localhost:8000/docs — Swagger UI

---

**🎵 Сохраняйте музыку без цензуры!**
