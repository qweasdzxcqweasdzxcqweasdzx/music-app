# 📋 Ultimate Music App - API Reference

Полный справочник всех API endpoints.

---

## 🔐 Аутентификация

### POST /api/auth/telegram
Вход через Telegram WebApp
```bash
curl -X POST "http://localhost:8000/api/auth/telegram" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "init_data=..."
```

### GET /api/me
Данные текущего пользователя (требуется токен)
```bash
curl "http://localhost:8000/api/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎵 Музыка

### GET /api/search
Поиск треков, артистов, альбомов
```bash
curl "http://localhost:8000/api/search?q=weeknd&limit=20&type=all"
```

**Параметры:**
- `q` — поисковый запрос (обязательно)
- `limit` — количество результатов (1-50)
- `type` — тип: all, tracks, artists, albums

### GET /api/search/unified
Единый поиск по всем источникам
```bash
curl "http://localhost:8000/api/search/unified?q=weeknd&sources=spotify,soundcloud,navidrome"
```

### GET /api/tracks/{track_id}
Информация о треке
```bash
curl "http://localhost:8000/api/tracks/spotify:track:123456"
```

### GET /api/tracks/{track_id}/stream
URL для стриминга трека
```bash
curl "http://localhost:8000/api/tracks/spotify:track:123456/stream"
```

### GET /api/tracks/{track_id}/lyrics
Текст песни
```bash
curl "http://localhost:8000/api/tracks/123/lyrics?track_title=Blinding+Lights&artist_name=The+Weeknd"
```

---

## 🎤 Артисты

### GET /api/artists/{artist_id}
Информация об артисте
```bash
curl "http://localhost:8000/api/artists/1Xyo4u8uXC1ZmMpatF05PJ"
```

### GET /api/artists/{artist_id}/tracks
Топ треки артиста
```bash
curl "http://localhost:8000/api/artists/1Xyo4u8uXC1ZmMpatF05PJ/tracks?limit=10"
```

### GET /api/artists/{artist_id}/albums
Альбомы и синглы
```bash
curl "http://localhost:8000/api/artists/1Xyo4u8uXC1ZmMpatF05PJ/albums?include_groups=album,single"
```

### GET /api/artists/{artist_id}/recommendations
Похожие артисты
```bash
curl "http://localhost:8000/api/artists/1Xyo4u8uXC1ZmMpatF05PJ/recommendations"
```

---

## 💿 Альбомы

### GET /api/albums/{album_id}
Информация об альбоме
```bash
curl "http://localhost:8000/api/albums/4yP0hdKOZPNshxUOjY0cZj"
```

### GET /api/albums/{album_id}/tracks
Треки альбома
```bash
curl "http://localhost:8000/api/albums/4yP0hdKOZPNshxUOjY0cZj/tracks?limit=50"
```

### GET /api/singles/{single_id}
Сингл (альбом с 1 треком)
```bash
curl "http://localhost:8000/api/singles/123456"
```

---

## 🎯 Рекомендации

### GET /api/recommendations
Рекомендации на основе seed
```bash
curl "http://localhost:8000/api/recommendations?seed_artists=1Xyo4u8uXC1ZmMpatF05PJ&seed_genres=pop&limit=20"
```

**Параметры:**
- `seed_artists` — CSV ID артистов (макс 5)
- `seed_tracks` — CSV ID треков (макс 5)
- `seed_genres` — CSV жанров (макс 5)
- `limit` — количество результатов

### GET /api/recommendations/for-you
Персональные рекомендации (требуется токен)
```bash
curl "http://localhost:8000/api/recommendations/for-you?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/recommendations/mood/{mood}
Рекомендации по настроению
```bash
curl "http://localhost:8000/api/recommendations/mood/chill?limit=20"
```

**Настроения:** happy, sad, energetic, chill, focus

---

## 🎼 Жанры

### GET /api/genres
Список всех жанров
```bash
curl "http://localhost:8000/api/genres"
```

### GET /api/genres/{genre_id}
Треки по жанру
```bash
curl "http://localhost:8000/api/genres/pop?limit=20"
```

---

## 📊 Чарты

### GET /api/top
Популярные треки
```bash
curl "http://localhost:8000/api/top?limit=20&country=US"
```

### GET /api/new
Новые релизы
```bash
curl "http://localhost:8000/api/new?limit=20"
```

### GET /api/featured
Популярные плейлисты
```bash
curl "http://localhost:8000/api/featured?limit=10"
```

---

## 🎚️ Smart Mixer (Умный миксер)

### GET /api/mixer/smart
Умный микс на основе предпочтений (требуется токен)
```bash
curl "http://localhost:8000/api/mixer/smart?limit=50&sources=spotify,soundcloud" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/mixer/radio/{track_id}
Бесконечное радио на основе трека
```bash
curl "http://localhost:8000/api/mixer/radio/spotify:track:123456?limit=50"
```

### GET /api/mixer/mood/{mood}
Микс по настроению
```bash
curl "http://localhost:8000/api/mixer/mood/energetic?limit=30"
```

### GET /api/mixer/genre/{genre}
Микс по жанру
```bash
curl "http://localhost:8000/api/mixer/genre/electronic?limit=40&sources=spotify,soundcloud"
```

---

## 🤖 AI Генерация

### POST /api/ai/generate
Генерация музыки через AI
```bash
curl -X POST "http://localhost:8000/api/ai/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "provider": "suno",
    "prompt": "A happy pop song about summer",
    "tags": "pop happy summer",
    "title": "Summer Vibes"
  }'
```

**Провайдеры:**
- `suno` — генерация песен
- `mubert` — фоновая музыка
- `musicgen` — короткие клипы

**Параметры:**
- `provider` — провайдер (обязательно)
- `prompt` — описание (обязательно)
- `tags` — теги (для Suno)
- `title` — название (для Suno)
- `duration` — длительность в секундах
- `mood` — настроение (для Mubert)
- `genre` — жанр (для Mubert)

### GET /api/ai/status/{task_id}
Статус задачи генерации
```bash
curl "http://localhost:8000/api/ai/status/TASK_ID?provider=suno"
```

### POST /api/ai/separate
Разделение трека на стемы
```bash
curl -X POST "http://localhost:8000/api/ai/separate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "audio_url": "https://example.com/track.mp3",
    "stem_type": "vocals"
  }'
```

**Типы стемов:** vocals, instrumental, drums, bass, guitar, piano

### POST /api/ai/voice
Синтез голоса
```bash
curl -X POST "http://localhost:8000/api/ai/voice" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "text": "Hello, this is a test",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'
```

### GET /api/ai/voices
Список доступных голосов
```bash
curl "http://localhost:8000/api/ai/voices?provider=elevenlabs"
```

---

## 📁 Плейлисты

### POST /api/playlists
Создать плейлист
```bash
curl -X POST "http://localhost:8000/api/playlists" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Playlist",
    "description": "My favorite tracks",
    "is_public": false
  }'
```

### GET /api/playlists
Мои плейлисты
```bash
curl "http://localhost:8000/api/playlists" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/playlists/{playlist_id}
Плейлист по ID
```bash
curl "http://localhost:8000/api/playlists/PLAYLIST_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### PUT /api/playlists/{playlist_id}
Обновить плейлист
```bash
curl -X PUT "http://localhost:8000/api/playlists/PLAYLIST_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Updated Name"
  }'
```

### DELETE /api/playlists/{playlist_id}
Удалить плейлист
```bash
curl -X DELETE "http://localhost:8000/api/playlists/PLAYLIST_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/playlists/{playlist_id}/tracks
Добавить трек в плейлист
```bash
curl -X POST "http://localhost:8000/api/playlists/PLAYLIST_ID/tracks?track_id=TRACK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### DELETE /api/playlists/{playlist_id}/tracks/{track_id}
Удалить трек из плейлиста
```bash
curl -X DELETE "http://localhost:8000/api/playlists/PLAYLIST_ID/tracks/TRACK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ❤️ Лайки

### GET /api/likes
Любимые треки
```bash
curl "http://localhost:8000/api/likes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/likes/{track_id}
Лайкнуть трек
```bash
curl -X POST "http://localhost:8000/api/likes/TRACK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### DELETE /api/likes/{track_id}
Удалить лайк
```bash
curl -X DELETE "http://localhost:8000/api/likes/TRACK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📜 История

### GET /api/history
История прослушиваний
```bash
curl "http://localhost:8000/api/history?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/history
Добавить в историю
```bash
curl -X POST "http://localhost:8000/api/history?track_id=TRACK_ID&play_duration=180" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎵 Daily Mixes & Discovery

### GET /api/daily-mixes
Ежедневные миксы (требуется токен)
```bash
curl "http://localhost:8000/api/daily-mixes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/release-radar
Новые релизы любимых артистов
```bash
curl "http://localhost:8000/api/release-radar" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/discover-weekly
Еженедельные открытия
```bash
curl "http://localhost:8000/api/discover-weekly" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Статистика

### GET /api/stats
Статистика пользователя
```bash
curl "http://localhost:8000/api/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎸 Источники

### GET /api/sources
Доступные источники музыки
```bash
curl "http://localhost:8000/api/sources"
```

---

## 🔌 WebSocket

### WS /ws
WebSocket для реального времени

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  // Аутентификация
  ws.send(JSON.stringify({
    type: 'auth',
    payload: {
      user_id: '123',
      token: 'YOUR_TOKEN'
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Присоединение к комнате (Jam сессия)
ws.send(JSON.stringify({
  type: 'join_room',
  payload: { room_id: 'ROOM_ID' }
}));

// Подписка на события
ws.send(JSON.stringify({
  type: 'subscribe',
  payload: { events: ['ai_generation_update', 'player_update'] }
}));
```

---

## 📁 Фоновые задачи (Celery)

### POST /api/tasks/generate-mix
Фоновая генерация микса
```bash
curl -X POST "http://localhost:8000/api/tasks/generate-mix?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /api/tasks/status/{task_id}
Статус задачи
```bash
curl "http://localhost:8000/api/tasks/status/TASK_ID"
```

---

## 🏥 Health & Status

### GET /health
Проверка здоровья
```bash
curl "http://localhost:8000/health"
```

### GET /
Информация о приложении
```bash
curl "http://localhost:8000/"
```

---

## 🔗 API Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

---

## 📝 Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## 🔒 Rate Limiting

- 60 запросов в минуту
- 1000 запросов в час

При превышении лимита возвращается код 429.
