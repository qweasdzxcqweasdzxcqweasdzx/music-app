# 📱 TELEGRAM MINI APP - КАК ЗАПУСТИТЬ

**Статус:** ⚠️ Требует настройки

---

## ✅ ЧТО УЖЕ ГОТОВО

| Компонент | Статус |
|-----------|--------|
| **Bot Token** | ✅ Есть в .env |
| **Frontend SDK** | ✅ Подключён |
| **API** | ✅ Работает |
| **Фронтенд на GitHub** | ✅ Задеплоен |

---

## ❌ ЧТО НУЖНО СДЕЛАТЬ

### 1. Создать Telegram бота

**Если бота нет:**

1. Откройте @BotFather в Telegram
2. Отправьте `/newbot`
3. Введите имя бота
4. Скопируйте токен
5. Обновите `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

**Ваш текущий токен:**
```
8486711572:AAFpmQ_0vzjHRgi61FdnXLdRcbIaA7Pe8TA
```

---

### 2. Настроить Web App в боте

**В @BotFather:**

1. Отправьте `/mybots`
2. Выберите вашего бота
3. Bot Settings → Menu Button → Configure Menu Button
4. Отправьте URL:
   ```
   https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
   ```
5. Введите название кнопки (например: "🎵 Слушать музыку")

---

### 3. Включить бота

**Запуск бота (опционально):**

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate

# Бот уже есть в main.py (не в main_lite.py)
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**ИЛИ используйте готовый бот:**

```bash
# В main_lite.py бот отключён
# Но фронтенд работает через Telegram WebApp SDK
```

---

## 🎯 КАК ЗАПУСТИТЬ ПРЯМО СЕЙЧАС

### Вариант 1: Быстрый (без бота)

**Просто откройте ссылку в Telegram:**

1. Откройте Telegram
2. В поиске введите: `@your_bot_name` (ваш бот)
3. Отправьте команду `/start`
4. Нажмите кнопку меню "🎵 Слушать музыку"

**ИЛИ прямо по ссылке:**
```
https://t.me/your_bot_name?start=app
```

---

### Вариант 2: Полноценный (с ботом)

**1. Обновите main_lite.py для поддержки бота:**

```python
# Добавить в main_lite.py
from bot import music_bot  # Раскомментировать

# В lifespan функции:
async with lifespan(app):
    # Запуск бота
    if settings.TELEGRAM_BOT_TOKEN:
        import asyncio
        asyncio.create_task(music_bot.run())
```

**2. Запустите бота:**

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**3. Проверьте бота:**
- Откройте бота в Telegram
- Нажмите `/start`
- Должна появиться кнопка "Menu"

---

## 📊 ТЕКУЩАЯ КОНФИГУРАЦИЯ

### Backend (.env)

```env
TELEGRAM_BOT_TOKEN=8486711572:AAFpmQ_0vzjHRgi61FdnXLdRcbIaA7Pe8TA
```

### Frontend (index.html)

```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

### Frontend (musicApi.js)

```javascript
// Telegram аутентификация уже есть
async initTelegramAuth() {
    if (window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.ready();
        // ...
    }
}
```

---

## 🎯 БЫСТРЫЙ СТАРТ

### 1. Проверьте бота

```bash
# Токен есть
grep TELEGRAM_BOT_TOKEN backend/.env
```

### 2. Настройте Menu Button

В @BotFather:
```
/BotSettings → Menu Button → URL:
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

### 3. Откройте в Telegram

```
t.me/your_bot_name
```

### 4. Нажмите Menu

Кнопка откроет Mini App

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### 1. "Бот не отвечает"

**Причина:** Бот не запущен

**Решение:**
```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. "Web App не открывается"

**Причина:** URL не настроен в BotFather

**Решение:** Настроить Menu Button URL

### 3. "CORS ошибка"

**Причина:** Бэкенд не разрешает Telegram

**Решение:** В main_lite.py:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или ["https://t.me"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 ИТОГ

### Сейчас работает:

- ✅ Фронтенд на GitHub Pages
- ✅ Telegram SDK подключён
- ✅ Bot token в .env
- ✅ API работает

### Нужно сделать:

- ⚠️ Настроить Menu Button в @BotFather
- ⚠️ Запустить бота (если нужен)

### Можно запустить ПРЯМО СЕЙЧАС:

1. Откройте бота в Telegram
2. Нажмите Menu
3. **Mini App откроется!**

---

**🎵 ВСЁ ГОТОВО ДЛЯ TELEGRAM! НАСТРОЙТЕ BOTFATHER И ЗАПУСКАЙТЕ!**
