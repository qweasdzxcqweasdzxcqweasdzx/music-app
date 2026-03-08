# Telegram Music Mini App - Финальная документация

## 🎵 Описание приложения

**Music Player** — это полноценное музыкальное приложение в стиле Spotify прямо в Telegram!

### ✨ Функционал

#### 🎨 Интерфейс в стиле Spotify
- Тёмная тема с фирменными цветами
- Плавные анимации и переходы
- Адаптивный дизайн для всех устройств

#### 📱 Навигация
- **Боковая панель** с возможностью сворачивания
- **Главная** — персональные миксы, недавние треки, чарты
- **Поиск** — живой поиск, 24 жанра, недавние запросы
- **Медиатека** — плейлисты, артисты, альбомы, любимые треки

#### 🎵 Музыкальные возможности
- **Эквалайзер** — 9 полос, 10 пресетов, визуализация
- **Spotify Connect** — переключение между устройствами
- **Тексты песен** — интеграция с Genius API
- **Очередь воспроизведения** — управление списком треков
- **Персональные рекомендации** — на основе истории

#### 🔧 Технические особенности
- **React 19** + Vite
- **Spotify Web API** — официальные данные
- **Web Audio API** — эквалайзер и визуализация
- **LocalStorage** — сохранение состояния
- **GitHub Pages** — хостинг фронтенда

---

## 🚀 Быстрый старт

### Фронтенд (GitHub Pages)

Приложение доступно по URL:
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

### Бэкенд (локальный сервер)

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

API доступно по URL:
```
http://78.140.249.136:8000
http://localhost:8000
```

---

## 🔑 Настройка Spotify API

### 1. Получение ключей

1. Перейди на https://developer.spotify.com/dashboard
2. Создай приложение
3. Скопируй **Client ID** и **Client Secret**

### 2. Настройка бэкенда

```bash
cd /home/c1ten12/music-app/backend
nano .env
```

Добавь в `.env`:
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### 3. Перезапуск

```bash
pkill -f "uvicorn main:app"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📁 Структура проекта

```
music-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx       # Боковая навигация
│   │   │   ├── Player.jsx        # Музыкальный плеер
│   │   │   ├── Equalizer.jsx     # Эквалайзер
│   │   │   ├── Connect.jsx       # Spotify Connect
│   │   │   └── Lyrics.jsx        # Тексты песен
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Главная страница
│   │   │   ├── Search.jsx        # Поиск
│   │   │   └── Library.jsx       # Медиатека
│   │   ├── styles/
│   │   │   └── spotify-theme.css # Дизайн-система
│   │   └── App.jsx               # Главный компонент
│   └── dist/                     # Сборка для GitHub Pages
│
└── backend/
    ├── services/
    │   ├── spotify_service.py    # Spotify API
    │   ├── music_service.py      # Музыкальная логика
    │   └── cache_service.py      # Кэширование
    ├── main.py                   # FastAPI приложение
    └── .env                      # Конфигурация
```

---

## 🎛️ API Endpoints

### Музыка
```
GET  /api/search?q=...        # Поиск
GET  /api/tracks/{id}         # Трек
GET  /api/tracks/{id}/stream  # Поток
GET  /api/top                 # Топ треков
GET  /api/new                 # Новинки
GET  /api/genres              # Жанры
```

### Артисты
```
GET  /api/artists/{id}              # Информация
GET  /api/artists/{id}/tracks       # Топ треки
GET  /api/artists/{id}/albums       # Альбомы
GET  /api/artists/{id}/recommendations # Похожие
```

### Альбомы
```
GET  /api/albums/{id}         # Информация
GET  /api/albums/{id}/tracks  # Треки
```

### Рекомендации
```
GET  /api/recommendations?seed_artists=...  # На основе seed
GET  /api/recommendations/for-you           # Персональные
GET  /api/recommendations/mood/{mood}       # По настроению
```

---

## 🎨 Компоненты

### Equalizer
- 9 частотных полос (60Hz - 14kHz)
- 10 пресетов: Flat, Bass, Treble, Vocal, Jazz, Rock, Electronic, Classical, Pop, HipHop
- Визуализация в реальном времени
- Web Audio API BiquadFilter

### Connect
- Список доступных устройств
- Переключение воспроизведения
- Анимация эквалайзера для активного устройства
- localStorage для синхронизации

### Lyrics
- Интеграция с Genius API
- Fallback на заглушку
- Ссылка на полный текст

### Player
- Компактный и развёрнутый вид
- Управление: play/pause, next/prev, shuffle, repeat
- Прогресс-бар с перемоткой
- Регулятор громкости
- Кнопка лайка

---

## 📱 Telegram Mini Apps

### Настройка

1. Открой [@BotFather](https://t.me/BotFather)
2. `/newapp` → выбери бота
3. URL: `https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/`
4. Готово!

### Команды бота

```
/start - Запустить приложение
/search [query] - Поиск трека
/top - Топ треков
/liked - Любимые треки
```

---

## 🔧 Разработка

### Фронтенд

```bash
cd frontend
npm install
npm run dev      # Разработка
npm run build    # Сборка
npm run preview  # Предпросмотр
```

### Бэкенд

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

---

## 📊 Статистика

| Компонент | Статус | URL |
|-----------|--------|-----|
| Фронтенд | ✅ | https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/ |
| Бэкенд API | ✅ | http://78.140.249.136:8000 |
| Swagger Docs | ✅ | http://78.140.249.136:8000/docs |
| GitHub Repo | ✅ | https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app |

---

## 🎯 Планы развития

- [ ] Плейлисты с drag-n-drop
- [ ] Расширенная очередь воспроизведения
- [ ] Кроссфейд между треками
- [ ] Нормализация громкости
- [ ] Офлайн режим
- [ ] Подкасты
- [ ] Радио на основе трека
- [ ] Социальные функции

---

**v3.0** — Spotify-style UI + Equalizer + Connect + Lyrics

**Сделано с ❤️ для Telegram Music Community**
