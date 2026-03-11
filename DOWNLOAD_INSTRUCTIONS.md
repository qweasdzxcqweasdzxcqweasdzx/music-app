# 📥 Инструкция по скачиванию треков

## ⚡ Быстрое скачивание (ручной способ)

### 1. Через yt-dlp с авторизацией VK:

```bash
# Установка
pip install yt-dlp

# Авторизация VK (получение cookies)
# 1. Зайди на vk.com в браузере
# 2. Скопируй cookies.txt (расширение Get cookies.txt)
# 3. Скачивание:

yt-dlp --cookies cookies.txt \
  -x --audio-format mp3 \
  -o "%(artist)s - %(title)s.%(ext)s" \
  "https://vk.com/audio_playlist123"
```

### 2. Через Telegram ботов:

```
@VKMusicBot - скачивание из VK
@YouTubeMusicBot - скачивание из YouTube
```

### 3. Скрипт для массового скачивания:

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Обновление базы URL (нужны прямые ссылки!)
python3 update_track_urls.py

# Скачивание
python3 download_uncensored_tracks.py
```

---

## 🎵 Список треков для скачивания

### Приоритет 1 (самые важные):

**OG Buda:**
- ОПГ сити
- Даёт 2
- Групи
- Выстрелы
- Грусть
- Добро Пожаловать
- Грязный

**Big Baby Tape:**
- Bandana I
- KOOP
- Benzo Gang Money
- So Icy Nihao

**Pharaoh:**
- Phuneral
- Правило

**Агата Кристи:**
- Опиум для никого
- Декаданс
- Ураган

### Приоритет 2:

**Платина:**
- Завидуют
- Актриса
- Братва на связи

**Soda Luv:**
- Голодный пес
- G-SHOKK
- КОТЬ!

**Lil Krystalll:**
- 2 бара
- Тик-так

---

## 🔍 Где искать треки:

### VK Music (основной источник):
```
https://vk.com/audios
```

### Yandex Music:
```
https://music.yandex.ru/
```

### YouTube (если доступно):
```
https://music.youtube.com/
```

### Telegram каналы:
```
@music_for_all
@free_music_channel
```

---

## 📁 Структура папок:

```
downloaded_tracks/
├── OG Buda/
│   ├── ОПГ сити.mp3
│   ├── Даёт 2.mp3
│   └── ...
├── Big Baby Tape/
│   ├── Bandana I.mp3
│   ├── KOOP.mp3
│   └── ...
├── Pharaoh/
│   ├── Phuneral.mp3
│   └── Правило.mp3
└── ...
```

---

## ⚠️ Проблема с YouTube

YouTube заблокировал скачивание из России. Решения:

1. **Использовать прокси:**
```bash
yt-dlp --proxy "http://proxy:port" ...
```

2. **Использовать VK Music вместо YouTube**

3. **Использовать зеркало Invidious:**
```bash
yt-dlp "https://inv.tux.piped.video/watch?v=VIDEO_ID"
```

---

## ✅ После скачивания:

1. **Переместить файлы** в папку backend/static/tracks/
2. **Обновить базу** с прямыми ссылками:
```json
{
  "stream_url": "/static/tracks/OG%20Buda%20-%20ОПГ%20сити.mp3"
}
```

3. **Перезапустить backend**

---

**🎯 ГЛАВНОЕ: СКАЧАТЬ ТРЕКИ НУЖНО СЕЙЧАС, ПОКА ОНИ ДОСТУПНЫ!**
