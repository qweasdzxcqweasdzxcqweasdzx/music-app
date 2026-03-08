# 🔊 Аудио - Документация

## Обзор

Реализовано воспроизведение аудио через HTML5 Audio API с поддержкой:
- Потоковое воспроизведение
- Очередь треков
- Переключение треков (вперёд/назад)
- Перемотка
- Регулировка громкости
- Повтор (all/one/off)
- Перемешивание (shuffle)
- Обработка ошибок
- Индикаторы загрузки

## Архитектура

```
PlayerContext (React Context)
    ├── HTML5 Audio (ref)
    ├── Состояние (useState)
    ├── Обработчики событий (event listeners)
    └── Методы управления
```

## PlayerContext

### Состояния

| Состояние | Тип | Описание |
|-----------|-----|----------|
| `currentTrack` | object | Текущий трек |
| `isPlaying` | boolean | Воспроизводится ли |
| `isLoading` | boolean | Загрузка буфера |
| `progress` | number | Текущая позиция (сек) |
| `duration` | number | Длительность трека (сек) |
| `volume` | number | Громкость (0-1) |
| `queue` | array[] | Очередь треков |
| `queueIndex` | number | Индекс текущего в очереди |
| `isLiked` | boolean | Добавлен в избранное |
| `isShuffle` | boolean | Перемешивание включено |
| `repeatMode` | string | Режим повтора ('off', 'all', 'one') |
| `error` | string | Ошибка (если есть) |

### Методы

```javascript
// Воспроизведение трека
playTrack(track, newQueue)

// Пауза/продолжение
togglePlay()

// Следующий трек
playNext()

// Предыдущий трек
playPrevious()

// Перемотка
seek(seconds)

// Громкость
setVolume(0-1)

// В избранное
toggleLike()

// Перемешивание
toggleShuffle()

// Повтор
toggleRepeat()
```

## Интеграция с бэкендом

### Структура трека

```javascript
{
  id: string,           // Уникальный ID
  title: string,        // Название
  artist: string,       // Исполнитель
  duration: number,     // Длительность в секундах
  stream_url: string,   // URL потока (MP3, M4A, etc.)
  cover: string,        // URL обложки
  explicit: boolean     // Явный контент
}
```

### Получение URL для воспроизведения

В `PlayerContext.jsx` замените функцию `getAudioUrl`:

```javascript
const getAudioUrl = (track) => {
  // Вместо тестовых URL используйте реальные
  return track.stream_url;
};
```

### Пример API ответа

```json
{
  "track": {
    "id": "track_123",
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "duration": 354,
    "stream_url": "https://api.example.com/stream/track_123",
    "cover": "https://api.example.com/covers/queen.jpg"
  }
}
```

## Обработка ошибок

### Типы ошибок HTML5 Audio

```javascript
const audio = new Audio();

audio.addEventListener('error', (e) => {
  switch (e.target.errorCode) {
    case 1: // MEDIA_ERR_ABORTED
      console.log('Воспроизведение прервано');
      break;
    case 2: // MEDIA_ERR_NETWORK
      console.log('Ошибка сети');
      break;
    case 3: // MEDIA_ERR_DECODE
      console.log('Ошибка декодирования');
      break;
    case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
      console.log('Формат не поддерживается');
      break;
  }
});
```

### Отображение ошибок

```jsx
{error && (
  <div className="errorMessage">
    <span>{error}</span>
    <button onClick={togglePlay}>Повторить</button>
  </div>
)}
```

## Индикаторы загрузки

### Состояния загрузки

1. **buffering** - Буферизация потока
2. **loading** - Загрузка метаданных
3. **playing** - Воспроизведение
4. **paused** - Пауза
5. **ended** - Трек завершён

### Визуализация

```jsx
// В MiniPlayer
{isLoading && (
  <div className="loadingSpinner">
    <svg>...</svg>
  </div>
)}

// В FullPlayer
{isLoading && (
  <div className="coverLoadingOverlay">
    <div className="spinner" />
  </div>
)}
```

## Прогресс воспроизведения

### Обновление прогресса

```javascript
// В PlayerContext
audio.addEventListener('timeupdate', () => {
  setProgress(audio.currentTime);
});

// Перемотка
const seek = (value) => {
  audio.currentTime = value;
  setProgress(value);
};
```

### Форматирование времени

```javascript
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
```

## Очередь воспроизведения

### Добавление в очередь

```javascript
const addToQueue = (tracks) => {
  setQueue(prev => [...prev, ...tracks]);
};
```

### Следующий трек

```javascript
const playNext = () => {
  const nextIndex = isShuffle
    ? Math.floor(Math.random() * queue.length)
    : (queueIndex < queue.length - 1 ? queueIndex + 1 : 0);
  
  setQueueIndex(nextIndex);
  setCurrentTrack(queue[nextIndex]);
};
```

## Громкость

### Установка громкости

```javascript
// В PlayerContext
useEffect(() => {
  if (audioRef.current) {
    audioRef.current.volume = volume;
  }
}, [volume]);
```

### UI для громкости

```jsx
<input
  type="range"
  min="0"
  max="1"
  step="0.01"
  value={volume}
  onChange={(e) => setVolume(parseFloat(e.target.value))}
/>
```

## Поддерживаемые форматы

HTML5 Audio поддерживает:

| Формат | MIME тип | Поддержка |
|--------|----------|-----------|
| MP3 | audio/mpeg | ✅ Все браузеры |
| AAC/M4A | audio/mp4 | ✅ Большинство |
| OGG | audio/ogg | ✅ Firefox, Chrome |
| WAV | audio/wav | ✅ Ограниченно |
| WebM | audio/webm | ✅ Chrome, Firefox |

### Проверка поддержки

```javascript
const audio = new Audio();

if (audio.canPlayType('audio/mpeg')) {
  console.log('MP3 поддерживается');
}

if (audio.canPlayType('audio/mp4; codecs="mp4a.40.2"')) {
  console.log('AAC поддерживается');
}
```

## Оптимизация

### Предзагрузка

```javascript
audio.preload = 'metadata'; // Только метаданные
audio.preload = 'auto';     // Полная предзагрузка
audio.preload = 'none';     // Без предзагрузки
```

### Кэширование

Используйте Service Worker для кэширования треков:

```javascript
// service-worker.js
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/stream/')) {
    event.respondWith(
      caches.open('audio').then((cache) => {
        return cache.match(event.request).then((response) => {
          return response || fetch(event.request);
        });
      })
    );
  }
});
```

## Telegram WebApp

### Интеграция

```javascript
import WebApp from '@twa-dev/sdk';

// Инициализация
useEffect(() => {
  WebApp.ready();
  WebApp.expand();
}, []);
```

### Ограничения

- Автовоспроизведение только после взаимодействия пользователя
- Ограничения на фоновое воспроизведение в iOS
- Требуется HTTPS для потоков

## Пример использования

```jsx
import { usePlayer } from './contexts/PlayerContext';

function MyComponent() {
  const { 
    currentTrack, 
    isPlaying, 
    isLoading,
    togglePlay,
    playNext,
    progress,
    duration
  } = usePlayer();

  return (
    <div>
      <h3>{currentTrack?.title}</h3>
      <p>{currentTrack?.artist}</p>
      
      {isLoading ? (
        <div>Загрузка...</div>
      ) : (
        <button onClick={togglePlay}>
          {isPlaying ? 'Pause' : 'Play'}
        </button>
      )}
      
      <progress value={progress} max={duration} />
      <span>{formatTime(progress)} / {formatTime(duration)}</span>
      
      <button onClick={playNext}>Next</button>
    </div>
  );
}
```

## Тестовые аудио URL

Для тестирования используются бесплатные семплы:

```javascript
const TEST_AUDIO_URLS = [
  'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
  'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
  // ...
];
```

## Следующие шаги

- [ ] Интеграция с VK Music API
- [ ] Интеграция с YouTube (через backend)
- [ ] Адаптивный битрейт
- [ ] Офлайн режим (кэширование)
- [ ] Эквалайзер
- [ ] Crossfade между треками
