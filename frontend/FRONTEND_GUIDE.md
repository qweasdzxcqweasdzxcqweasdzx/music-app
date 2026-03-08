# 🎨 Frontend Ultimate Music App v3.0

## 📦 Обновлённый стек

- **React 19** - последняя версия
- **React Router DOM v7** - навигация
- **Vite** - сборка
- **CSS Modules** - изоляция стилей

---

## 📁 Новые компоненты

### Страницы

| Страница | Файл | Описание |
|----------|------|----------|
| **AI Studio** | `pages/AIStudio.jsx` | Генерация музыки через AI |
| **Smart Mixer** | `pages/SmartMixer.jsx` | Умные миксы |
| **Sources** | `pages/Sources.jsx` | Управление источниками |
| **Artist** | `pages/Artist.jsx` | Страница артиста |
| **Album** | `pages/Album.jsx` | Страница альбома |
| **DailyMixes** | `pages/DailyMixes.jsx` | Daily Mixes |
| **FullPlayer** | `pages/FullPlayer.jsx` | Полноэкранный плеер |
| **Stats** | `pages/Stats.jsx` | Статистика |

### Контексты

| Контекст | Файл | Описание |
|----------|------|----------|
| **PlayerContext** | `contexts/PlayerContext.jsx` | Управление плеером |

### API

| Модуль | Файл | Описание |
|--------|------|----------|
| **MusicAPI** | `api/musicApi.js` | Клиент API (обновлён) |

---

## 🎵 PlayerContext API

```javascript
import { useContext } from 'react';
import { PlayerContext } from './contexts/PlayerContext';

function MyComponent() {
  const {
    // Состояние
    currentTrack,
    isPlaying,
    isLoading,
    progress,
    duration,
    volume,
    isMuted,
    shuffle,
    repeat,
    queue,
    queueIndex,
    
    // Управление
    playTrack,
    togglePlay,
    nextTrack,
    prevTrack,
    seek,
    setVolume,
    toggleMute,
    toggleShuffle,
    toggleRepeat,
    
    // Очередь
    addToQueue,
    removeFromQueue,
    clearQueue,
    playQueue,
    
    // Утилиты
    formatTime,
    clearLyrics,
  } = useContext(PlayerContext);
}
```

---

## 🔌 MusicAPI методы

### Поиск
```javascript
// Обычный поиск
await musicAPI.search('weeknd', 20, 'all');

// Единый поиск по всем источникам
await musicAPI.unifiedSearch('weeknd', 20, ['spotify', 'soundcloud']);
```

### Smart Mixer
```javascript
// Умный микс
await musicAPI.getSmartMix(50, ['spotify', 'navidrome']);

// Бесконечное радио
await musicAPI.getInfiniteRadio('spotify:track:123', 50);

// Микс по настроению
await musicAPI.getMoodMix('chill', 30);

// Микс по жанру
await musicAPI.getGenreMix('electronic', 40, ['spotify']);
```

### AI Генерация
```javascript
// Генерация музыки
await musicAPI.generateMusic('suno', 'happy pop song', {
  tags: 'pop summer',
  title: 'Summer Vibes',
});

// Статус генерации
await musicAPI.getGenerationStatus('task_id', 'suno');

// Разделение на стемы
await musicAPI.separateStems('https://...', 'vocals');

// Синтез голоса
await musicAPI.generateVoice('Hello world', 'voice_id');
```

---

## 📱 Навигация

### Основное меню
- 🏠 Главная
- 🔍 Поиск
- 📚 Медиатека

### Музыка
- 🎚️ Smart Mixer
- 🤖 AI Студия
- 📅 Daily Mixes

### Библиотека
- ❤️ Любимые треки
- 🎵 Очередь

### Настройки
- 🔌 Источники
- 📊 Статистика
- 🎛️ Эквалайзер

---

## 🎨 Темы и стили

### Цветовая палитра
```css
:root {
  /* Фон */
  --bg-primary: #121212;
  --bg-secondary: #1a1a1a;
  --bg-elevated: #242424;
  
  /* Текст */
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  
  /* Акцент */
  --accent: #1db954;
  --accent-hover: #1ed760;
  
  /* Градиенты */
  --gradient-primary: linear-gradient(135deg, #1db954, #8e44ad);
  --gradient-ai: linear-gradient(135deg, #1db954, #e74c3c);
}
```

---

## 🚀 Быстрый старт

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка production
npm run build

# Предпросмотр сборки
npm run preview
```

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| Страниц | 13+ |
| Компонентов | 20+ |
| API методов | 50+ |
| CSS модулей | 15+ |

---

## 🎯 Ключевые улучшения

### ✅ PlayerContext
- Централизованное управление
- Плавное затухание (fade in/out)
- Автоматическая история
- Загрузка текстов

### ✅ MusicAPI
- Поддержка всех endpoints
- WebSocket для реального времени
- Авто-реконнект
- Обработка ошибок

### ✅ UI/UX
- Адаптивный дизайн
- Плавные анимации
- Скелетоны загрузки
- Уведомления

### ✅ Новые страницы
- AI Studio - генерация музыки
- Smart Mixer - умные миксы
- Sources - управление источниками

---

## 📝 Примеры использования

### Воспроизведение трека
```javascript
const { playTrack } = useContext(PlayerContext);

const track = {
  id: 'spotify:track:123',
  title: 'Blinding Lights',
  artist: 'The Weeknd',
  stream_url: 'https://...',
  cover: 'https://...',
  duration: 200,
};

playTrack(track);
```

### Добавление в очередь
```javascript
const { addToQueue } = useContext(PlayerContext);

addToQueue(track);
```

### Генерация микса
```javascript
const mix = await musicAPI.getSmartMix(50, ['spotify', 'soundcloud']);
playTrack(mix.tracks[0], mix.tracks);
```

---

## 🐛 Известные ограничения

- WebSocket требует запущенного backend
- AI генерация требует API ключей
- Некоторые функции требуют аутентификации

---

**v3.0** — Ultimate Frontend с AI и Smart Mixer
