# 🎵 Ultimate Music App - Frontend

React-фронтенд для музыкальной платформы с Anti-Censorship системой.

**Демо:** https://yourusername.github.io/music-app/

---

## ⚡ Быстрый старт

### 1. Настройка API URL

Откройте `src/api/musicApi.js` и измените URL на ваш сервер:

```javascript
// src/api/musicApi.js

// ❌ Было (localhost)
// const API_URL = 'http://localhost:8000/api';

// ✅ Стало (ваш сервер)
const API_URL = 'http://YOUR_SERVER_IP:8000/api';

// Или с доменом
// const API_URL = 'https://your-domain.com/api';
```

### 2. Сборка

```bash
npm install
npm run build
```

### 3. Деплой на GitHub Pages

```bash
# Установка gh-pages
npm install --save-dev gh-pages

# Добавление в package.json scripts:
# "deploy": "gh-pages -d dist"

# Деплой
npm run deploy
```

---

## 🔧 Настройка

### Переменные окружения

Создайте `.env` в корне фронтенда:

```env
VITE_API_URL=http://YOUR_SERVER_IP:8000/api
VITE_TELEGRAM_BOT_NAME=your_bot_name
```

### API endpoints

Основные endpoints:

| Endpoint | Описание |
|----------|----------|
| `GET /health` | Проверка сервера |
| `GET /api/censorship/check` | Проверка трека |
| `POST /api/censorship/find-original` | Поиск оригинала |
| `GET /api/censorship/search-uncensored` | Поиск explicit версий |

---

## 🚀 Деплой

### GitHub Pages

1. Обновите `musicApi.js` с вашим API URL
2. Запустите `npm run build`
3. Задеплойте `dist/` папку

```bash
git add dist/
git commit -m "Build for deployment"
git push
```

### Vercel

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

---

## 📦 Технологии

- **React 19** - UI библиотека
- **Vite** - Сборщик
- **React Router DOM** - Роутинг
- **TWA SDK** - Telegram интеграция

---

## 🔗 Ссылки

- **Бэкенд:** http://YOUR_SERVER_IP:8000
- **Swagger UI:** http://YOUR_SERVER_IP:8000/docs
- **Документация бэкенда:** /backend/DEPLOYMENT.md

---

## 📝 License

MIT
