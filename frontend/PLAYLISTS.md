# 🎵 Плейлисты - Документация

## Обзор

Страница плейлиста позволяет:
- Просматривать треки в плейлисте
- Воспроизводить треки
- Редактировать название и описание
- Удалять треки
- Создавать новые плейлисты

## Маршруты

| URL | Описание |
|-----|----------|
| `/playlist/favorites` | Любимые треки |
| `/playlist/workout` | Для тренировок |
| `/playlist/car` | В машину |
| `/playlist/new` | Создание нового плейлиста |

## Компоненты

### Playlist.jsx

**Основные функции:**
- `handlePlay()` - воспроизведение всех треков
- `handleEdit()` - режим редактирования
- `handleSave()` - сохранение изменений
- `handleDeleteTrack()` - удаление трека

**Режимы:**
1. **Просмотр** - отображение треков, управление воспроизведением
2. **Редактирование** - изменение названия, описания, обложки

## Моковые данные

```javascript
const mockPlaylists = {
  'favorites': {
    id: 'favorites',
    name: 'Любимое',
    description: 'Ваши любимые треки',
    cover: 'https://picsum.photos/seed/favorites/300/300',
    isPublic: false,
    tracks: [...]
  },
  // ...
};
```

## Интеграция с бэкендом

Для подключения реального API замените моковые данные на запросы:

```javascript
// Загрузка плейлиста
const response = await fetch(`/api/playlists/${id}`);
const playlist = await response.json();

// Сохранение изменений
await fetch(`/api/playlists/${id}`, {
  method: 'PUT',
  body: JSON.stringify(editData)
});

// Удаление трека
await fetch(`/api/playlists/${id}/tracks/${trackId}`, {
  method: 'DELETE'
});
```

## Стили

Основные CSS классы в `Playlist.module.css`:
- `.playlist` - контейнер
- `.header` - шапка с градиентом
- `.cover` - обложка 200x200
- `.trackList` - список треков
- `.editMode` - режим редактирования
