# 📋 План доработок Telegram Music Mini App

## 🔴 Критичные ошибки (срочно)

### 1. PlayerContext - нет импорта asyncio
**Файл**: `frontend/src/contexts/PlayerContext.jsx`
**Проблема**: Отсутствует обработка ошибок API
**Решение**: Добавить try-catch и fallback на тестовые URL

### 2. Album.jsx - отсутствует CSS импорт
**Файл**: `frontend/src/pages/Album.jsx`
**Проблема**: Нет импорта стилей
**Решение**: Проверить наличие Album.module.css ✓ (создан)

### 3. Artist.jsx - битые импорты иконок
**Файл**: `frontend/src/pages/Artist.jsx`
**Проблема**: BackIcon может отсутствовать в Icons.jsx
**Решение**: Добавить иконку в Icons.jsx

## 🟡 Функции Spotify (приоритет)

### 1. Connect Device (Spotify Connect)
**Оригинал**: Управление воспроизведением на других устройствах
**Реализация**:
- API endpoint `/api/devices` - список устройств
- API endpoint `/api/transfer-playback` - переключение
- Frontend: кнопка выбора устройства в плеере

### 2. Lyrics (Тексты песен)
**Оригинал**: Musixmatch интеграция
**Реализация**:
- API endpoint `/api/tracks/{id}/lyrics`
- Сервис для Genius/Musixmatch API
- Frontend: вкладка "Текст" в FullPlayer

### 3. Queue (Очередь воспроизведения)
**Оригинал**: Просмотр и управление очередью
**Реализация**:
- API endpoint `/api/queue` - текущая очередь
- API endpoint `/api/queue/add` - добавить в очередь
- Frontend: страница Queue с списком треков

### 4. Daily Mixes
**Оригинал**: Персональные миксы на каждый день
**Реализация**:
- API endpoint `/api/daily-mixes`
- Генерация на основе истории за 30 дней
- Frontend: секция на главной

### 5. Release Radar
**Оригинал**: Новые релизы любимых артистов
**Реализация**:
- API endpoint `/api/release-radar`
- Фильтрация новых релизов по топ артистам
- Frontend: отдельная страница/секция

### 6. Discover Weekly
**Оригинал**: Еженедельные рекомендации
**Реализация**:
- API endpoint `/api/discover-weekly`
- Алгоритм на основе collaborative filtering
- Frontend: отдельный плейлист

### 7. Flow (Непрерывное воспроизведение)
**Оригинал**: Автопродолжение похожими треками
**Реализация**:
- В PlayerContext: автозагрузка рекомендаций
- Когда очередь заканчивается - добавлять похожие

### 8. Crossfade
**Оригинал**: Плавный переход между треками
**Реализация**:
- Web Audio API для fade in/out
- Настройка длительности (0-12 сек)

### 9. Gapless Playback
**Оригинал**: Без задержек между треками
**Реализация**:
- Preload следующего трека
- Buffer management

### 10. Social Features
**Оригинал**: Совместное прослушивание
**Реализация**:
- WebSocket для синхронизации
- API endpoint `/api/jam` - сессии
- Frontend: страница Jam Session

## 🟢 Улучшения UX

### 1. Skeleton Loading
**Оригинал**: Анимация загрузки контента
**Реализация**:
- Компонент Skeleton
- Замена spinner на skeleton

### 2. Haptic Feedback
**Оригинал**: Вибрация при действиях
**Реализация**:
- Telegram HapticFeedback API
- При лайке, переключении трека

### 3. Smart Shuffle
**Оригинал**: Умное перемешивание
**Реализация**:
- Алгоритм с учётом темпа, жанра
- Чередование популярных и редких треков

### 4. Recently Played
**Оригинал**: Быстрый доступ к недавним
**Реализация**:
- Секция на главной
- Кэширование последних 10 треков

### 5. Enhanced Search
**Оригинал**: Поиск с категориями
**Реализация**:
- Табы: Все, Треки, Артисты, Альбомы
- Recent searches с обложками

## 📊 Метрики и аналитика

### 1. Listening Stats
**Оригинал**: Spotify Wrapped
**Реализация**:
- API endpoint `/api/stats`
- Топ артисты, жанры, минуты
- Frontend: страница статистики

### 2. Year in Review
**Оригинал**: Итоги года
**Реализация**:
- Агрегация данных за год
- Визуализация в стиле Wrapped

## 🔄 Оптимизации

### 1. Image Lazy Loading
**Реализация**:
- loading="lazy" для изображений
- Intersection Observer

### 2. API Response Caching
**Реализация**:
- Redis кэширование
- TTL для разных endpoints

### 3. Prefetching
**Реализация**:
- Предзагрузка следующего трека
- Предзагрузка страниц артистов

## 📝 Приоритеты

1. **Сейчас**: Исправление критичных ошибок
2. **Сегодня**: Connect Device + Queue
3. **Эта неделя**: Lyrics + Daily Mixes
4. **Следующая неделя**: Discover Weekly + Flow
5. **Потом**: Social features + Stats
