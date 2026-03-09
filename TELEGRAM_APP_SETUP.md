# 📱 Telegram Mini App - Полная настройка

## ✅ Что работает

| Компонент | Статус |
|-----------|--------|
| Telegram WebApp SDK | ✅ Интегрирован |
| Аутентификация | ✅ Через initData |
| Темизация | ✅ Авто-темизация |
| MainButton | ✅ Настроена |
| BackButton | ✅ Работает |

---

## 🚀 Быстрый старт

### 1. Запустите приложение

```bash
cd /home/c1ten12/music-app
./stable-run.sh
```

Дождитесь получения Cloudflare URL.

### 2. Создайте Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Введите имя бота: `Music App`
4. Введите username: `music_app_bot`
5. Скопируйте токен бота

### 3. Настройте Mini App

1. Отправьте @BotFather: `/newapp`
2. Выберите вашего бота
3. Введите название: `Music Player`
4. Введите описание: `Слушайте музыку в Telegram`
5. Загрузите фото (640x360)
6. **Вставьте URL:** `https://YOUR-CLOUDFLARE-URL.trycloudflare.com`
7. Введите short name: `music`

### 4. Проверка

Откройте: `https://t.me/YOUR_BOT_USERNAME/music`

---

## 🔧 Настройка бэкенда для Telegram

### Добавьте токен бота в .env

```bash
cd /home/c1ten12/music-app/backend
nano .env
```

Добавьте:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Перезапустите бэкенд

```bash
./stop.sh
./stable-run.sh
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│  Telegram Mini App                                  │
│  WebApp SDK                                         │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────────┐
│  Cloudflare Tunnel                                  │
│  https://xxx.trycloudflare.com                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  CORS Proxy (порт 8081)                             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Backend API (порт 8000)                            │
│  - Telegram Auth                                    │
│  - Music Search                                     │
│  - Audio Streaming                                  │
└─────────────────────────────────────────────────────┘
```

---

## 📡 API для Telegram

### Аутентификация

```javascript
// Фронтенд получает initData из Telegram
const tg = window.Telegram.WebApp;
const initData = tg.initData;

// Отправка на бэкенд
fetch('/api/auth/telegram', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `init_data=${encodeURIComponent(initData)}`
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('token', data.access_token);
});
```

### Получение пользователя

```javascript
fetch('/api/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(user => {
  console.log('User:', user);
});
```

---

## 🎨 UI компоненты для Telegram

### TabBar (нижняя навигация)

Автоматически адаптируется под Telegram:
- Цвета из темы Telegram
- Safe areas для iOS
- Haptic feedback

### MainButton

```javascript
const tg = window.Telegram.WebApp;

// Настройка кнопки
tg.MainButton.setText("ВОСПРОИЗВЕСТИ");
tg.MainButton.onClick(() => {
  // Действие
});
tg.MainButton.show();
```

### BackButton

```javascript
tg.BackButton.onClick(() => {
  window.history.back();
});
tg.BackButton.show();
```

---

## 🔍 Отладка

### Логи в Telegram

```javascript
// Отправка логов в консоль Telegram
console.log('Debug info:', data);

// Показ alert пользователю
tg.showAlert('Произошла ошибка');

// Подтверждение
tg.showConfirm('Вы уверены?', (confirmed) => {
  if (confirmed) {
    // Действие
  }
});
```

### Проверка работы

1. Откройте бота в Telegram
2. Нажмите `/start`
3. Откройте Mini App
4. Проверьте консоль разработчика

---

## 🛠️ Проблемы и решения

### Проблема: "Invalid initData"

**Решение:** Проверьте SECRET_KEY в .env

### Проблема: CORS ошибки

**Решение:** Убедитесь что CORS proxy работает:
```bash
curl http://localhost:8081/api/censorship/test
```

### Проблема: Cloudflare отключается

**Решение:** Перезапустите:
```bash
./stable-run.sh
```

### Проблема: Бот не открывает приложение

**Решение:** Проверьте URL в @BotFather - должен быть HTTPS

---

## 📊 Мониторинг

### Проверка статусов

```bash
./status.sh
```

### Логи

```bash
tail -f /tmp/music-app/backend.log
tail -f /tmp/music-app/cors.log
tail -f /tmp/music-app/cloudflared.log
```

### Telegram бот логи

```bash
cd /home/c1ten12/music-app/backend
tail -f /tmp/bot.log
```

---

## 🎯 Чеклист настройки

- [ ] Бот создан в @BotFather
- [ ] Mini App настроен
- [ ] URL вставлен (Cloudflare)
- [ ] TELEGRAM_BOT_TOKEN в .env
- [ ] Приложение запущено (./stable-run.sh)
- [ ] Тест в Telegram пройден

---

## 🔗 Ссылки

- [Telegram WebApp SDK](https://core.telegram.org/bots/webapps)
- [BotFather](https://t.me/BotFather)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**✅ ГОТОВО! Ваш музыкальный бот в Telegram работает!**
