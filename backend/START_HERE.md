# 🎵 НАЧНИТЕ ЗДЕСЬ!

## ✅ ЧТО УЖЕ ГОТОВО

1. **База цензурированных треков** - 4 трека
2. **Локальный музыкальный сервер** - запущен на порту 8080
3. **Скрипты для скачивания** - готовы к использованию

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Скачивание uncensored треков

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Скачать 5 треков из базы
python download_uncensored_massive.py --from-db --limit 5 --explicit
```

### 2. Проверка статуса

```bash
# Статистика базы
curl http://localhost:8080/api/stats

# Все треки
curl http://localhost:8080/api/tracks
```

### 3. Воспроизведение

Откройте в браузере:
```
http://localhost:8080
```

---

## 📊 ВАША БАЗА СЕЙЧАС

```
Всего треков: 4
• Billie Eilish - Bad Guy (Clean Version)
• Eminem - Lose Yourself (blurred)
• Ed Sheeran - Shape of You (muted)
• Test Artist - Test Censored Track
```

---

## 📥 КОМАНДЫ ДЛЯ СКАЧИВАНИЯ

### Скачать все треки из базы:
```bash
python download_uncensored_massive.py --from-db --limit 10 --explicit
```

### Скачать конкретного артиста:
```bash
python -c "
import yt_dlp
ydl_opts = {'format': 'bestaudio', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/results?search_query=Eminem+Lose+Yourself+explicit'])
"
```

### Через Telegram:
```bash
python telegram_auto_download.py
```

---

## 🔧 УПРАВЛЕНИЕ СЕРВЕРОМ

### Запуск:
```bash
python local_music_server.py --port 8080 --scan
```

### Остановка:
```bash
pkill -f local_music_server
```

### Перезапуск со сканированием:
```bash
pkill -f local_music_server
python local_music_server.py --port 8080 --scan
```

---

## 📡 API ENDPOINTS

| URL | Описание |
|-----|----------|
| http://localhost:8080/api/stats | Статистика |
| http://localhost:8080/api/tracks | Все треки |
| http://localhost:8080/api/search?q=... | Поиск |
| http://localhost:8080/api/random | Случайные |
| http://localhost:8080/music/Artist/Track.mp3 | Прямая ссылка |

---

## 📚 ПОЛНАЯ ДОКУМЕНТАЦИЯ

- `LOCAL_MUSIC_SETUP.md` - Полная инструкция
- `QUICKSTART_CENSORED.md` - Быстрый старт
- `INSTRUCTION_CENSORED_TRACKS.md` - Детальная документация

---

**🎵 ПРИЯТНОГО ПРОСЛУШИВАНИЯ!**
