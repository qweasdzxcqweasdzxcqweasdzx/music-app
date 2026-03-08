# 🤖 Промт для продолжения работы над Telegram Music Mini App

## Контекст проекта

Ты работаешь над **Telegram Music Mini App v2.0** — полноценным музыкальным стримингом в Telegram с системой анти-цензуры.

### Стек технологий
- **Фронтенд**: React 18 + Vite + React Router DOM + Telegram WebApp SDK
- **Бэкенд**: FastAPI + MongoDB + Redis + JWT
- **Источники музыки**: VK Music API (основной), YouTube через yt-dlp (резерв + оригиналы)
- **Telegram**: Mini App + Bot + Inline режим
- **Docker**: MongoDB, Redis, Backend, Nginx

### Структура проекта
```
музыкавтг/
├── frontend/src/
│   ├── api/musicApi.js        # API клиент
│   ├── contexts/PlayerContext.jsx  # Плеер
│   ├── pages/                 # Страницы
│   └── components/            # Компоненты
├── backend/
│   ├── services/
│   │   ├── music_service.py   # Фасад + анти-цензура
│   │   ├── vk_service.py      # VK API
│   │   └── youtube_service.py # YouTube (yt-dlp)
│   ├── bot.py                 # Telegram бот
│   ├── main.py                # FastAPI приложение
│   ├── routes.py              # API endpoints
│   └── .env                   # Конфигурация
└── docker-compose.yml
```

## ✅ Что уже реализовано (v2.0)

### Бэкенд
- ✅ **VK Music Service** — поиск треков через VK API
- ✅ **YouTube Service** — поиск через yt-dlp, получение stream URL
- ✅ **CensorshipDetector** — детекция цензурированных версий
- ✅ **Anti-Censorship System** — автоматическая замена на оригиналы
- ✅ **Telegram Bot** — команды (/start, /search, /top, /genre, /help)
- ✅ **Inline режим** — поиск музыки прямо в чатах
- ✅ **API endpoints** — /search, /top, /new, /genres, /playlists, /likes, /history
- ✅ **JWT Authentication** — через Telegram WebApp initData

### Фронтенд
- ✅ **PlayerContext** — управление плеером (очередь, repeat, shuffle)
- ✅ **API Client** — musicApi.js с методами для всех endpoints
- ✅ **Страница Search** — поиск с реальным API
- ✅ **Страница Home** — топ треков, новинки, недавно прослушано
- ✅ **Telegram интеграция** — тема, WebApp Auth

### Инфраструктура
- ✅ **Docker Compose** — MongoDB, Redis, Backend, Nginx
- ✅ **Dockerfile** — сборка бэкенда с FFmpeg и yt-dlp
- ✅ **.env.example** — шаблон конфигурации

## 🔧 Что требует доработки

### Приоритет 1 (Критичное)

#### 1. Настройка VK OAuth
**Файл**: `backend/services/vk_service.py`

**Проблема**: Требуется правильная настройка OAuth для VK API.

**Задача**:
- Реализовать получение токена через Implicit Flow
- Обработать refresh токена
- Добавить обработку ошибок API

**VK API Docs**: https://dev.vk.com/ru/api/access_token/implicit-flow

```python
# Примерный код
async def _get_access_token(self):
    # 1. Проверка кэша
    if self.access_token and not self._is_expired():
        return self.access_token
    
    # 2. Запрос нового токена
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://oauth.vk.com/token',
            data={
                'grant_type': 'implicit_flow',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
            }
        ) as resp:
            data = await resp.json()
            self.access_token = data['access_token']
            self.expires_in = data['expires_in']
            return self.access_token
```

#### 2. Обработка stream URL для YouTube
**Файл**: `backend/services/youtube_service.py`

**Проблема**: YouTube не даёт прямой URL на аудио поток без загрузки.

**Задача**:
- Реализовать загрузку и стриминг через временные файлы
- Или использовать proxy для обхода CORS
- Кэширование загруженных треков в Redis

```python
async def get_track_stream(self, track_id: str) -> Optional[str]:
    # 1. Проверка кэша в Redis
    cached = await redis.get(f"stream:{track_id}")
    if cached:
        return cached
    
    # 2. Загрузка через yt-dlp
    # 3. Сохранение во временный файл
    # 4. Отдача файла через FileResponse
    # 5. Кэширование URL
```

#### 3. Подключение фронтенда к API
**Файл**: `frontend/src/contexts/PlayerContext.jsx`

**Проблема**: Требуется тестирование реальных вызовов API.

**Задача**:
- Протестировать аутентификацию через Telegram
- Проверить получение stream URL
- Обработать ошибки сети

### Приоритет 2 (Важное)

#### 4. База данных треков
**Файл**: `backend/routes.py`, `backend/models.py`

**Задача**:
- Сохранение найденных треков в MongoDB (кэширование)
- Индексация для быстрого поиска
- Сбор статистики (play_count)

```python
# models.py
class CachedTrack(BaseModel):
    vk_id: str
    title: str
    artist: str
    duration: int
    stream_url: str
    cover: Optional[str]
    source: str = "vk"
    is_explicit: bool = False
    play_count: int = 0
    last_played: datetime
```

#### 5. Топ треков (реальная статистика)
**Файл**: `backend/routes.py`

**Задача**:
- Endpoint `/api/top` с сортировкой по play_count
- Агрегация через MongoDB
- Кэширование результатов в Redis

```python
@router.get("/top")
async def get_top_tracks(limit: int = 20):
    tracks_collection = await get_collection("tracks")
    
    top = await tracks_collection.find()\
        .sort("play_count", -1)\
        .limit(limit)\
        .to_list(length=limit)
    
    return {"tracks": top, "total": len(top)}
```

#### 6. Страница артиста
**Файл**: `frontend/src/pages/Artist.jsx`, `backend/routes.py`

**Задача**:
- Реальный вызов API для получения информации об артисте
- Отображение треков, альбомов, похожих артистов
- Кнопка "Слушать все"

### Приоритет 3 (Улучшения)

#### 7. Тексты песен
**Файл**: `backend/services/lyrics_service.py` (создать)

**Источники**:
- Genius API (неофициально)
- Lyrics.ovh
- Tekstowo.pl

```python
async def get_lyrics(artist: str, title: str) -> Optional[str]:
    async with aiohttp.get(
        f"https://lyrics.ovh/{artist}/{title}"
    ) as resp:
        data = await resp.json()
        return data.get('lyrics')
```

#### 8. Рекомендации на основе истории
**Файл**: `backend/services/recommendation_service.py` (создать)

**Алгоритм**:
1. Анализ прослушанных треков
2. Поиск похожих артистов
3. Фильтрация уже прослушанных
4. Возврат рекомендаций

#### 9. Премиум подписка
**Файл**: `backend/models.py`, `backend/routes.py`

**Функции**:
- Флаг `is_premium` в модели User
- Endpoint для покупки подписки
- Расширенные лимиты (больше треков в очереди, offline режим)

## 📋 Инструкции для продолжения

### Если продолжаешь с предыдущего места:

1. **Проверь последнюю задачу** в todo list
2. **Посмотри логи** если что-то не работает:
   ```bash
   docker-compose logs -f backend
   ```
3. **Проверь API** через Swagger: http://localhost:8000/docs

### Для тестирования:

1. **Запуск бэкенда**:
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Запуск фронтенда**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Проверка бота**:
   - Открой бота в Telegram
   - Отправь `/start`
   - Нажми "🎵 Открыть плеер"

4. **Проверка inline режима**:
   - В любом чате напиши `@your_bot_name queen`
   - Должны появиться результаты поиска

### Контекст для конкретных задач:

#### Задача: Настройка VK API

```python
# 1. Получи client_id и client_secret
# https://vk.com/dev/implicit_flow_user

# 2. Обнови backend/.env
VK_CLIENT_ID=xxxxx
VK_CLIENT_SECRET=xxxxx

# 3. Протестируй поиск
curl "http://localhost:8000/api/search?q=queen&limit=5"
```

#### Задача: Тестирование анти-цензуры

```python
# 1. Найди трек с маркером "clean" или "radio"
from services.music_service import music_service

tracks = await music_service.search("radio edit", limit=5)

# 2. Проверь детекцию
for track in tracks:
    is_censored = await music_service.check_censorship(track)
    print(f"{track.title}: censored={is_censored}")
    
    # 3. Попробуй найти оригинал
    if is_censored:
        original = await music_service.get_original_version(track)
        if original:
            print(f"  -> Оригинал: {original.title}")
```

#### Задача: Фронтенд API calls

```javascript
// frontend/src/api/musicApi.js уже содержит все методы

// Пример использования в компоненте:
import { musicAPI } from '../api/musicApi';

const searchTracks = async () => {
  try {
    const data = await musicAPI.search('queen', 20);
    console.log('Tracks:', data.tracks);
  } catch (error) {
    console.error('Search error:', error);
  }
};
```

## 🎯 Текущая задача

[ЗДЕСЬ УКАЗЫВАЙ КОНКРЕТНУЮ ЗАДАЧУ]

Примеры формулировок:
- "Реализуй получение VK OAuth токена через Implicit Flow"
- "Добавь кэширование треков в MongoDB"
- "Исправь ошибку получения stream URL для YouTube"
- "Создай компонент Lyrics для отображения текста песен"
- "Добавь агрегацию для endpoint /api/top"

## ⚠️ Важные замечания

### Безопасность
- Не коммить `.env` файлы
- SECRET_KEY должен быть уникальным в продакшене
- Telegram initData проверяется через HMAC-SHA256

### Производительность
- Кэшируй результаты поиска в Redis
- Используй индексы MongoDB для частых запросов
- Lazy loading для изображений

### Юридические аспекты
- Проект для личного/образовательного использования
- Для продакшена использовать официальные API (Spotify, Apple Music)
- VK API — неофициальный, риск блокировки

## 📚 Ресурсы

- [VK API Documentation](https://dev.vk.com/ru/method/audio)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram WebApp](https://core.telegram.org/bots/webapps)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

**Готов к работе! Укажи задачу и я помогу с реализацией 🚀**
