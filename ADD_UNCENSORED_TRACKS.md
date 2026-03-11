# 📝 Как добавлять треки в базу Uncensored Finder

## 🎯 Быстрое добавление через API

### 1. Через curl (командная строка):

```bash
curl -X POST "http://localhost:8081/api/uncensored/add-pair" \
  -H "Content-Type: application/json" \
  -d '{
    "censored_title": "Название (Clean Version)",
    "uncensored_title": "Название (Explicit)",
    "artist": "Исполнитель",
    "stream_url": "https://youtube.com/watch?v=...",
    "source": "youtube"
  }'
```

### 2. Через Python скрипт:

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python3 add_uncensored_pairs.py
```

### 3. Редактирование файла базы:

Файл: `backend/uncensored_pairs.json`

```json
{
  "md5_hash_clean_title": {
    "clean_title": "Bad Guy",
    "uncensored_title": "Bad Guy (Explicit)",
    "artist": "Billie Eilish",
    "stream_url": "https://youtube.com/watch?v=...",
    "source": "youtube",
    "created_at": 0
  }
}
```

---

## 📋 Список добавленных треков

### Русские артисты:

| Артист | Clean Версия | Original Версия | Источник |
|--------|-------------|-----------------|----------|
| Агата Кристи | Опиум для никого (Radio Edit) | Опиум для никого | YouTube |
| Психея | Убей мента (Clean) | Убей мента | YouTube |
| OG Buda | ОПГ сити (Radio) | ОПГ сити | VK |
| OG Buda | Даёт 2 (Clean) | Даёт 2 | VK |
| OG Buda | Групи (Radio) | Групи | VK |
| OG Buda | Выстрелы (Clean) | Выстрелы | VK |
| OG Buda | Грусть (Radio) | Грусть | VK |
| OG Buda | Добро Пожаловать (Clean) | Добро Пожаловать | VK |
| Big Baby Tape | Bandana (Clean) | Bandana | VK |
| Big Baby Tape | KOOP (Clean) | KOOP | VK |
| Платина | Завидуют (Radio Edit) | Завидуют | VK |
| Платина | Актриса (Clean) | Актриса | VK |
| Платина | Братва на связи (Radio) | Братва на связи | VK |
| Lil Krystalll | 2 бара (Clean) | 2 бара | VK |
| Lil Krystalll | Тик-так (Radio Edit) | Тик-так | VK |
| Soda Luv | Голодный пес (Radio) | Голодный пес | VK |
| Scally Milano | Даёт 2 (Clean) | Даёт 2 | VK |

### Международные артисты:

| Артист | Clean Версия | Original Версия | Источник |
|--------|-------------|-----------------|----------|
| Eminem | Lose Yourself (Radio Edit) | Lose Yourself | YouTube |
| Eminem | Godzilla (Clean) | Godzilla (feat. Juice WRLD) | YouTube |
| Billie Eilish | Bad Guy (Clean Version) | Bad Guy | YouTube |

---

## 🔍 Как найти uncensored версию самостоятельно

### 1. Поиск на YouTube:

```
{artist} {track name} explicit
{artist} {track name} original
{artist} {track name} uncensored
{artist} {track name} album version
```

### 2. Поиск на SoundCloud:

```
{artist} {track name} original
{artist} {track name} explicit
```

### 3. Поиск на VK Music:

VK часто имеет оригинальные версии:
- Открой VK Music
- Найди трек
- Скопируй ссылку на аудио

---

## 📝 Шаблон для добавления

Скопируй и заполни:

```json
{
  "censored_title": "Название (Clean/Radio Edit)",
  "uncensored_title": "Название (Original/Explicit)",
  "artist": "Исполнитель",
  "stream_url": "https://youtube.com/... или https://vk.com/audio/...",
  "source": "youtube/vk/soundcloud"
}
```

---

## ⚠️ Важные замечания

1. **Не все треки имеют цензурные версии**
   - Многие треки из твоего списка просто удалены/недоступны
   - Это не то же самое что clean/explicit версии

2. **Признаки clean версии:**
   - `(Clean Version)` в названии
   - `(Radio Edit)` в названии
   - `(Edited)` в названии
   - `(For Radio)` в названии

3. **Признаки explicit версии:**
   - `(Explicit)` в названии
   - `(Original)` в названии
   - `(Uncut)` в названии
   - `(Album Version)` в названии

---

## 🧪 Проверка работы

```bash
# Проверка трека
curl "http://localhost:8081/api/uncensored/check?track_id=1&title=Lose+Yourself+(Radio+Edit)&artist=Eminem"

# Поиск uncensored
curl "http://localhost:8081/api/uncensored/find?track_id=1&title=Lose+Yourself+(Radio+Edit)&artist=Eminem"
```

---

## 📊 Статистика базы

```bash
cd /home/c1ten12/music-app/backend
cat uncensored_pairs.json | python3 -c "import sys,json; print(f'В базе: {len(json.load(sys.stdin))} пар')"
```

---

**🎵 ДОБАВЛЯЙ НОВЫЕ ПАРЫ И ПОЛЬЗУЙСЯ!**
