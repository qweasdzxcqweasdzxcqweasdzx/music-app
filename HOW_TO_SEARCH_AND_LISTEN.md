# 🎵 КАК ИСКАТЬ И СЛУШАТЬ ТРЕКИ

**Статус:** ✅ Поиск работает | ⚠️ Прослушивание через VLC

---

## ✅ ПОИСК ТРЕКОВ - РАБОТАЕТ

### Через API

**Поиск с explicit приоритетом:**
```bash
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele&prefer_explicit=true"
```

**Пример ответа:**
```json
{
  "tracks": [
    {
      "track": {
        "title": "adele hello",
        "artist": "Adele",
        "source": "youtube",
        "stream_url": "https://www.youtube.com/watch?v=..."
      },
      "is_explicit": false,
      "version_type": "unknown"
    }
  ],
  "total": 5
}
```

### Через фронтенд

1. Откройте: https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
2. Введите запрос в поиске
3. Нажмите Enter

---

## ⚠️ ПРОСЛУШИВАНИЕ - ЧЕРЕЗ VLC

### Почему не в браузере?

**Проблема:** YouTube блокирует прямое воспроизведение в браузере из-за CORS

**Решение:** Использовать VLC плеер или скачать трек

---

### Вариант 1: VLC плеер (рекомендуется)

**Шаг 1: Найти трек**
```bash
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele"
```

**Шаг 2: Получить video_id из ответа**
```json
{
  "stream_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```
video_id = `dQw4w9WgXcQ`

**Шаг 3: Получить аудио URL**
```bash
curl "http://192.168.31.97:8000/audio/stream/dQw4w9WgXcQ"
```

**Ответ:**
```json
{
  "stream_url": "https://rr5---sn-...googlevideo.com/videoplayback?..."
}
```

**Шаг 4: Открыть в VLC**
1. VLC → Media → Open Network Stream
2. Вставить `stream_url`
3. Play

---

### Вариант 2: Скачать трек

**Получить аудио URL:**
```bash
AUDIO_URL=$(curl -s "http://192.168.31.97:8000/audio/stream/dQw4w9WgXcQ" | python3 -c "import sys,json; print(json.load(sys.stdin).get('stream_url', ''))")
```

**Скачать:**
```bash
curl -L "$AUDIO_URL" -o track.mp3
```

---

### Вариант 3: YouTube прямо (без API)

**Просто открыть YouTube:**
```
https://www.youtube.com/results?search_query=adele+hello
```

---

## 📝 API Endpoints для поиска

### Поиск треков

```bash
GET /api/censorship/search-uncensored?q={query}&prefer_explicit=true&limit=20
```

**Пример:**
```bash
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=eminem&prefer_explicit=true&limit=5"
```

### Проверка на цензуру

```bash
GET /api/censorship/check?track_id={id}&source={source}
```

### Поиск оригинала

```bash
POST /api/censorship/find-original
Content-Type: application/json

{"track_id": "123", "source": "youtube"}
```

---

## 🎯 Быстрые команды

### Поиск

```bash
# Найти трек
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q={название}"

# С фильтром explicit
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q={название}&prefer_explicit=true"
```

### Получить URL для VLC

```bash
# Получить audio URL
curl "http://192.168.31.97:8000/audio/stream/{video_id}"

# Извлечь URL
curl -s "http://192.168.31.97:8000/audio/stream/{video_id}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('stream_url', ''))"
```

---

## ⚠️ Возможные проблемы

### 1. "Not Found" на /audio/stream

**Причина:** Endpoint требует обновления

**Решение:** Использовать YouTube напрямую

### 2. CORS ошибка в браузере

**Причина:** YouTube блокирует CORS

**Решение:** VLC или скачать

### 3. URL истекает

**Причина:** YouTube URL действителен ~6 часов

**Решение:** Получить новый URL

---

## 📊 Итог

| Функция | Статус | Как использовать |
|---------|--------|------------------|
| **Поиск** | ✅ | API или фронтенд |
| **Audio URL** | ⚠️ | Через API |
| **Стриминг в браузере** | ❌ | CORS блокировка |
| **Стриминг в VLC** | ✅ | Open Network Stream |
| **Скачивание** | ✅ | curl -L URL -o track.mp3 |

---

## 🎵 Пример полного цикла

```bash
# 1. Поиск
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele&limit=1"

# 2. Извлечь video_id
# Из ответа: "stream_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# video_id = dQw4w9WgXcQ

# 3. Получить аудио URL
curl "http://192.168.31.97:8000/audio/stream/dQw4w9WgXcQ"

# 4. Открыть в VLC
# Media → Open Network Stream → Вставить URL

# ИЛИ скачать
curl -L "https://..." -o adele.mp3
```

---

**✅ ПОИСК РАБОТАЕТ!**

**⚠️ ПРОСЛУШИВАНИЕ:** Через VLC или скачивание
