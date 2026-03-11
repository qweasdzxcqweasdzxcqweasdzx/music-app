# 🎵 СПИСОК ТРЕКОВ ДЛЯ СКАЧИВАНИЯ

## 📋 СПИСОК ИЗ 20 ТРЕКОВ

Этот список находится в `telegram_auto_download.py`:

```python
TRACKS = [
    "OG Buda ОПГ сити",
    "OG Buda Даёт 2",
    "OG Buda Групи",
    "OG Buda Выстрелы",
    "OG Buda Грусть",
    "OG Buda Добро Пожаловать",
    "OG Buda Грязный",
    "Big Baby Tape Bandana I",
    "Big Baby Tape KOOP",
    "Big Baby Tape So Icy Nihao",
    "Pharaoh Phuneral",
    "Pharaoh Правило",
    "Агата Кристи Опиум для никого",
    "Агата Кристи Декаданс",
    "Агата Кристи Ураган",
    "Платина Завидуют",
    "Платина Актриса",
    "Soda Luv Голодный пес",
    "Soda Luv G-SHOKK",
    "Lil Krystalll 2 бара",
    "Lil Krystalll Тик-так",
]
```

---

## ⚠️ ПРОБЛЕМА

**YouTube не доступен** через yt-dlp из-за SSL ошибки (блокировка).

---

## ✅ РЕШЕНИЯ

### Способ 1: Telegram Боты (РЕКОМЕНДУЕТСЯ)

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python telegram_auto_download.py
```

**Что нужно сделать:**
1. Запустить скрипт
2. Ввести ваш номер Telegram (например, `+79991234567`)
3. Получить код в Telegram
4. Ввести код в терминал
5. Скрипт автоматически скачает все 20 треков

**Боты которые используются:**
- `@vk_music_bot`
- `@SaveMusicBot`
- `@GoMusicBot`

---

### Способ 2: Ручное скачивание через Telegram

1. Откройте Telegram
2. Найдите бота: `@vk_music_bot` или `@SaveMusicBot`
3. Отправьте боту название трека (например: `OG Buda ОПГ сити`)
4. Бот пришлёт файл
5. Сохраните файл в папку: `/home/c1ten12/music-app/backend/music_library/`

**Повторите для каждого трека из списка.**

---

### Способ 3: Через браузер + перемещение

1. Откройте YouTube в браузере
2. Найдите трек (например: `OG Buda ОПГ сити`)
3. Скачайте через онлайн сервис (например, y2mate.com)
4. Переместите файл в папку `music_library/`

---

### Способ 4: С Proxy

Если у вас есть proxy:

```bash
# В .env добавьте
PROXY_URL=http://proxy-server:port

# Или в скрипте
export HTTPS_PROXY=http://proxy-server:port
python download_track_list.py
```

---

## 📁 КУДА СОХРАНЯТЬ

```
/home/c1ten12/music-app/backend/music_library/
├── OG_Buda/
│   ├── ОПГ_сити.mp3
│   ├── Даёт_2.mp3
│   └── ...
├── Big_Baby_Tape/
│   ├── Bandana_I.mp3
│   └── ...
└── ...
```

---

## 🔄 ПОСЛЕ СКАЧИВАНИЯ

1. **Перезапустите сервер:**
```bash
pkill -f local_music_server
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python local_music_server.py --port 8080 --scan
```

2. **Проверьте треки:**
```bash
curl http://localhost:8080/api/tracks
```

3. **Слушайте:**
```
http://localhost:8080
```

---

## 📊 ТЕКУЩАЯ БИБЛИОТЕКА

```bash
curl -s http://localhost:8080/api/tracks | python3 -m json.tool
```

**Сейчас в библиотеке:** 3 тестовых трека

---

## 🎯 БЫСТРЫЙ СТАРТ

```bash
# 1. Запуск скачивания через Telegram
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python telegram_auto_download.py

# 2. Введите номер Telegram
# 3. Введите код из Telegram
# 4. Ждите пока скачаются все 20 треков
# 5. Перезапустите сервер
pkill -f local_music_server && python local_music_server.py --port 8080 --scan &

# 6. Проверьте
curl http://localhost:8080/api/stats
```

---

**🎵 ДЛЯ СКАЧИВАНИЯ ЗАПУСТИТЕ: `python telegram_auto_download.py`**
