# 🎵 Telegram Music Mini App

**SoundCloud-style музыкальное приложение в Telegram**

[![Deploy to GitHub Pages](https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app/actions/workflows/deploy.yml/badge.svg)](https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Возможности

### 🎨 Интерфейс в стиле SoundCloud
- Тёмная тема с оранжевыми акцентами
- Плавные анимации и переходы
- Адаптивный дизайн для всех устройств

### 🎵 Музыкальные функции
- **Эквалайзер** — 9 полос, 10 пресетов, визуализация
- **Очередь воспроизведения** — управление списком треков
- **Кроссфейд** — плавные переходы между треками
- **Плейлисты** — создание, редактирование, drag-n-drop
- **Лайки** — сохранение любимых треков
- **История** — отслеживание прослушиваний

### 🔗 Интеграции
- **Device Connect** — переключение между устройствами
- **Genius API** — тексты песен
- **SoundCloud API** — поиск и рекомендации
- **Telegram WebApp** — запуск в Telegram

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
http://music-app-telegram.loca.lt (HTTPS)
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
│   │   │   ├── Connect.jsx       # Device Connect
│   │   │   ├── Lyrics.jsx        # Тексты песен
│   │   │   └── Queue.jsx         # Очередь
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Главная
│   │   │   ├── Search.jsx        # Поиск
│   │   │   ├── Library.jsx       # Медиатека
│   │   │   └── PlaylistDetail.jsx # Плейлист
│   │   └── styles/
│   │       └── soundcloud-theme.css # Дизайн-система
│   └── .github/workflows/
│       └── deploy.yml            # GitHub Actions
│
└── backend/
    ├── services/
    │   ├── soundcloud_service.py    # SoundCloud API
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

### Документация
```
GET  /docs                  # Swagger UI
GET  /openapi.json          # OpenAPI spec
```

---

## 🔑 Настройка API

### SoundCloud API

1. Перейди на https://soundcloud.com/you/apps
2. Создай приложение
3. Скопируй Client ID и Client Secret
4. Обнови `backend/.env`:
   ```env
   SOUNDCLOUD_CLIENT_ID=your_client_id
   SOUNDCLOUD_CLIENT_SECRET=your_client_secret
   ```

### Genius API

1. Перейди на https://genius.com/api_clients
2. Создай приложение
3. Скопируй токен
4. Обнови `backend/.env`:
   ```env
   GENIUS_API_TOKEN=your_token
   ```

Подробная инструкция в [API_SETUP.md](API_SETUP.md)

---

## 🛠️ Разработка

### Фронтенд

```bash
cd frontend
npm install
npm run dev      # Разработка (http://localhost:5173)
npm run build    # Сборка
npm run preview  # Предпросмотр
```

### Бэкенд

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

---

## 📊 Статус

| Компонент | Статус | URL |
|-----------|--------|-----|
| Фронтенд | ✅ | https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/ |
| Бэкенд API | ✅ | http://78.140.249.136:8000 |
| Swagger Docs | ✅ | http://78.140.249.136:8000/docs |
| HTTPS Tunnel | ✅ | https://music-app-telegram.loca.lt |
| GitHub Repo | ✅ | https://github.com/qweasdzxcqweasdzxcqweasdzx/music-app |

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
/queue - Очередь воспроизведения
```

---

## 🎯 Реализованный функционал

- [x] SoundCloud-style UI
- [x] Навигация (Home, Search, Library)
- [x] Эквалайзер (9 полос, 10 пресетов)
- [x] Device Connect
- [x] Тексты песен (Genius)
- [x] Очередь воспроизведения
- [x] Плейлисты с drag-n-drop
- [x] Кроссфейд
- [x] Лайки
- [x] История прослушиваний
- [x] Персональные рекомендации (UI)
- [x] Поиск по жанрам
- [x] Адаптивный дизайн

---

## 📄 Лицензия

[MIT License](LICENSE)

---

## 🙏 Благодарности

- Дизайн вдохновлён [SoundCloud](https://soundcloud.com)
- API: [SoundCloud API](https://developers.soundcloud.com/docs/api/guide)
- Тексты: [Genius API](https://docs.genius.com)

---

**v3.0** — SoundCloud-style UI + Equalizer + Connect + Queue + Crossfade

**Сделано с ❤️ для Telegram Music Community**
