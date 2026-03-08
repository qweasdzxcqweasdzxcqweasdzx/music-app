# 🚀 Telegram Mini App - Руководство по запуску

## 📋 Требования

- Node.js 18+
- Backend запущен на порту 8000
- Telegram аккаунт для создания бота

---

## 🔧 Быстрый старт

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Настройка окружения

Создайте файл `.env` в папке `frontend`:

```env
VITE_API_URL=http://localhost:8000/api
```

Или для продакшена:

```env
VITE_API_URL=https://your-backend.com/api
```

### 3. Запуск разработки

```bash
npm run dev
```

Приложение доступно по: http://localhost:5173

### 4. Сборка для продакшена

```bash
npm run build
```

Файлы сборки в папке `dist/`

---

## 📱 Настройка Telegram Mini App

### Шаг 1: Создание бота

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Введите имя и username бота
4. Сохраните токен бота

### Шаг 2: Создание Mini App

1. В @BotFather отправьте `/newapp`
2. Выберите вашего бота
3. Введите название приложения
4. Введите описание
5. Загрузите фото (640x360px)
6. **Важно**: Введите URL вашего приложения

### Шаг 3: URL для Mini App

**Для разработки:**
- Используйте [ngrok](https://ngrok.com/) или [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- Пример: `https://your-tunnel.ngrok.io`

```bash
# Установка ngrok
npm install -g ngrok

# Запуск туннеля
ngrok http 5173
```

**Для продакшена:**
- GitHub Pages: `https://username.github.io/music-app/`
- Vercel: `https://your-app.vercel.app`
- Netlify: `https://your-app.netlify.app`

### Шаг 4: Настройка Web App URL

В @BotFather:
1. Отправьте `/setmenubutton`
2. Выберите бота
3. Отправьте URL вашего приложения

---

## 🌐 Деплой на GitHub Pages

### 1. Сборка

```bash
npm run build
```

### 2. Деплой через gh-pages

```bash
npm install -D gh-pages

# Добавляем в package.json:
# "homepage": "https://username.github.io/music-app",
# "scripts": {
#   "predeploy": "npm run build",
#   "deploy": "gh-pages -d dist"
# }

npm run deploy
```

### 3. Включение GitHub Pages

1. Settings → Pages
2. Source: GitHub Actions
3. URL: `https://username.github.io/music-app/`

---

## 🎨 Интеграция с Telegram

### Темизация

Приложение автоматически использует тему Telegram:

```javascript
const tg = window.Telegram.WebApp

// Цвета темы
const theme = tg.themeParams

// Установка цвета хедера
tg.setHeaderColor('#121212')

// Разворачивание на весь экран
tg.expand()
```

### MainButton

Использование главной кнопки Telegram:

```javascript
const tg = window.Telegram.WebApp

tg.MainButton.setText('ВОСПРОИЗВЕСТИ')
tg.MainButton.onClick(() => {
  // Действие
})
tg.MainButton.show()
```

### BackButton

Кнопка назад:

```javascript
const tg = window.Telegram.WebApp

tg.BackButton.onClick(() => {
  window.history.back()
})
tg.BackButton.show()
```

---

## 🔐 Аутентификация

Приложение автоматически аутентифицируется через Telegram:

```javascript
// В musicApi.js
async initTelegramAuth() {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    const initData = tg.initData
    
    if (initData) {
      await this.authTelegram(initData)
    }
  }
}
```

---

## 📱 Мобильная адаптация

### TabBar

Нижняя навигация для мобильных:

- Главная
- Поиск
- Медиатека
- Миксер

### Safe Areas

Поддержка iPhone с челкой:

```css
padding-left: env(safe-area-inset-left);
padding-right: env(safe-area-inset-right);
padding-bottom: env(safe-area-inset-bottom);
```

---

## 🐛 Отладка

### Консоль в Telegram

1. Отправьте @BotFather `/setinline`
2. Включите inline режим
3. В любом чате: `@yourbot debug`

### Remote Debugging

**Chrome DevTools:**
1. Откройте `chrome://inspect`
2. Найдите ваше приложение
3. Нажмите "Inspect"

---

## ✅ Чеклист перед запуском

- [ ] Backend настроен и доступен
- [ ] SoundCloud API ключи в `.env`
- [ ] Telegram бот создан
- [ ] Mini App URL настроен
- [ ] Сборка проходит без ошибок
- [ ] Мобильная версия протестирована
- [ ] Аутентификация работает

---

## 📊 Метрики

### Производительность

```bash
npm run build
# Проверить размер бандла
```

Целевые показатели:
- Initial load: < 3s
- First Contentful Paint: < 1.5s
- Bundle size: < 500KB

---

## 🆘 Troubleshooting

### "initData is undefined"

Убедитесь что приложение открыто в Telegram

### CORS ошибки

Проверьте настройки CORS в backend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### "401 Unauthorized"

Проверьте токен аутентификации в localStorage

---

**v3.0** — SoundCloud API + Telegram Mini App Ready
