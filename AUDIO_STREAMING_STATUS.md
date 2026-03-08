# 🎵 ВОЗМОЖНОСТИ ПРОСЛУШИВАНИЯ МУЗЫКИ

**Статус:** ⚠️ Частично реализовано

---

## ✅ Что работает

### 1. Поиск треков
**Статус:** ✅ Полностью работает

```bash
# Поиск с explicit приоритетом
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele&prefer_explicit=true"
```

**Результат:**
```json
{
  "tracks": [
    {
      "track": {
        "title": "adele hello",
        "artist": "Adele",
        "stream_url": "https://www.youtube.com/watch?v=...",
        "source": "youtube"
      },
      "is_explicit": false,
      "version_type": "unknown"
    }
  ]
}
```

### 2. Anti-Censorship
**Статус:** ✅ Полностью работает

- Распознавание clean/explicit версий
- Поиск оригинальных версий
- Fuzzy matching названий

### 3. Фронтенд
**Статус:** ✅ Доступен

- https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
- API URL настроен

---

## ⚠️ Стриминг (воспроизведение)

### Текущая ситуация

**Проблема:** YouTube требует дополнительной обработки для получения прямого аудио URL

**Причины:**
1. YouTube использует защищённые URL с токенами
2. URL истекают через несколько часов
3. Требуется обход CORS для браузерного воспроизведения

### Что реализовано

#### Endpoint для получения аудио URL

```bash
GET /audio/stream/{video_id}
```

**Пример:**
```bash
curl "http://192.168.31.97:8000/audio/stream/dQw4w9WgXcQ"
```

**Ответ:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "stream_url": "https://rr5---sn-...googlevideo.com/videoplayback?...",
  "duration": 212,
  "title": "Song Title",
  "artist": "Artist Name",
  "format": "audio only",
  "quality": 1
}
```

#### Endpoint для прямого воспроизведения

```bash
GET /audio/play/{video_id}
```

**Пример:**
```bash
curl -L "http://192.168.31.97:8000/audio/play/dQw4w9WgXcQ"
```

Перенаправляет на прямой аудио URL.

---

## 🔧 Как слушать музыку

### Вариант 1: Через API (для разработчиков)

```bash
# 1. Найти трек
curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=eminem"

# 2. Получить аудио URL
curl "http://192.168.31.97:8000/audio/stream/{video_id}"

# 3. Скачать или воспроизвести
curl -L "{stream_url}" -o track.mp3
```

### Вариант 2: VLC плеер

1. Найти трек через API
2. Получить stream_url
3. Открыть VLC: Media → Open Network Stream
4. Вставить URL

### Вариант 3: Браузер (требует доработки)

**Проблема:** CORS блокирует прямое воспроизведение

**Решение:** Нужен proxy или CORS заголовок на сервере

---

## 📊 Статус функционала

| Функция | Статус | Примечание |
|---------|--------|------------|
| **Поиск треков** | ✅ | YouTube работает |
| **Anti-Censorship** | ✅ | Все функции |
| **Получение audio URL** | ⚠️ | Работает нестабильно |
| **Прямой стриминг** | ❌ | Требует proxy/CORS |
| **Плейлисты** | ❌ | Требуется MongoDB |
| **Стриминг в браузере** | ❌ | CORS блокировка |

---

## 🛠️ Что нужно для полноценного стриминга

### 1. CORS Proxy

Добавить proxy для обхода CORS:

```python
# В routes_lite.py
@app.get("/proxy/audio")
async def proxy_audio(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return Response(
                await resp.read(),
                headers={'Content-Type': 'audio/mpeg'}
            )
```

### 2. ffmpeg для конвертации

```bash
sudo apt install ffmpeg
pip install ffmpeg-python
```

### 3. Кэширование URL

YouTube URL истекают через ~6 часов. Нужно кэшировать и обновлять.

---

## 📝 Рекомендации

### Для тестирования

1. **Поиск треков:**
   ```bash
   curl "http://192.168.31.97:8000/api/censorship/search-uncensored?q=adele"
   ```

2. **Получение URL:**
   ```bash
   curl "http://192.168.31.97:8000/audio/stream/{video_id}"
   ```

3. **Воспроизведение через VLC:**
   - Скопировать stream_url
   - Открыть в VLC

### Для продакшена

1. Добавить CORS proxy
2. Настроить кэширование URL
3. Добавить ffmpeg для конвертации
4. Реализовать адаптивный стриминг (HLS/DASH)

---

## 🎯 Итог

**✅ Можно:**
- Искать треки
- Получать информацию о цензуре
- Находить оригинальные версии
- Получать audio URL (для скачивания)

**⚠️ Ограничения:**
- Прямое воспроизведение в браузере требует CORS proxy
- URL истекают через несколько часов
- Требуется дополнительная обработка для стабильности

**❌ Не работает:**
- Стриминг в браузере "из коробки"
- Плейлисты (без MongoDB)

---

**Для полноценного прослушивания рекомендуется:**
1. Использовать VLC или другой плеер с URL
2. Или скачать трек через curl
3. Для браузера нужен CORS proxy
