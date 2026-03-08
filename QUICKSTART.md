# 🚀 Быстрый запуск Telegram Music Mini App

## 1. Получение Spotify API ключей (5 минут)

1. Перейди на https://developer.spotify.com/dashboard
2. Войди через Spotify аккаунт (или создай)
3. Нажми **"Create App"**
4. Заполни:
   - **App name**: `Telegram Music App`
   - **App description**: `Music streaming in Telegram`
   - **Redirect URI**: `http://localhost:8000/callback`
   - Отметь галочки **Web Playback** и **Client Credentials**
5. Нажми **Save**
6. Скопируй **Client ID** и **Client Secret**

## 2. Настройка проекта (2 минуты)

### Бэкенд
```bash
cd backend
cp .env.example .env
```

Открой `.env` и вставь:
```env
SPOTIFY_CLIENT_ID=твои_client_id_из_dashboard
SPOTIFY_CLIENT_SECRET=твои_client_secret_из_dashboard

# Опционально Telegram бот
TELEGRAM_BOT_TOKEN=
```

### Фронтенд
```bash
cd frontend
cp .env.example .env 2>/dev/null || echo "VITE_API_URL=http://localhost:8000/api" > .env
```

## 3. Запуск (3 минуты)

### Терминал 1 - Бэкенд
```bash
cd backend
pip install fastapi uvicorn python-multipart python-jose passlib python-telegram-bot aiohttp pydantic-settings python-dotenv bcrypt pymongo motor

# Запуск
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Проверка**: Открой http://localhost:8000/docs - должна открыться Swagger документация.

### Терминал 2 - Фронтенд
```bash
cd frontend
npm install
npm run dev
```

**Проверка**: Открой http://localhost:5173 - должна загрузиться главная страница.

## 4. Тестирование (1 минута)

### Проверка API
```bash
# Здоровье
curl http://localhost:8000/health

# Поиск
curl "http://localhost:8000/api/search?q=queen"

# Топ треков
curl http://localhost:8000/api/top

# Жанры
curl http://localhost:8000/api/genres
```

### Проверка фронтенда
1. Открой http://localhost:5173
2. Должна появиться главная страница с:
   - Быстрыми фильтрами (Поп, Рок, Хип-хоп...)
   - Секцией "Популярное сейчас"
   - Топ треков
   - Новинки
3. Кликни на трек - должно начаться воспроизведение
4. Кликни на артиста - откроется страница артиста
5. Кликни на альбом - откроется страница альбома

## 🐛 Решение проблем

### Ошибка: "ModuleNotFoundError: No module named 'fastapi'"
**Решение**: 
```bash
pip install fastapi uvicorn python-multipart python-jose passlib python-telegram-bot aiohttp pydantic-settings python-dotenv bcrypt pymongo motor
```

### Ошибка: "Port 8000 is already in use"
**Решение**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Или используй другой порт
python -m uvicorn main:app --port 8001
```

### Ошибка: "npm is not recognized"
**Решение**: Установи Node.js с https://nodejs.org/

### Фронтенд не подключается к API
**Решение**: Проверь что в `frontend/.env` указано:
```
VITE_API_URL=http://localhost:8000/api
```

### Spotify API возвращает ошибки
**Решение**: 
1. Проверь что Client ID и Secret правильные
2. Подожди 5 минут после создания приложения в Spotify Dashboard
3. Проверь что Redirect URI указан правильно

## 📱 Telegram интеграция (опционально)

### Создание бота
1. Открой @BotFather в Telegram
2. Отправь `/newbot`
3. Придумай имя (например: `Music Test Bot`)
4. Придумай username (например: `test_music_bot`)
5. Скопируй токен
6. Вставь токен в `backend/.env`:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Настройка Mini App
1. Отправь @BotFather команду `/newapp`
2. Выбери своего бота
3. Укажи URL: `http://localhost:8000/static/index.html`
4. Придумай короткое имя для кнопки

### Запуск бота
```bash
cd backend
python bot.py
```

## ✅ Чеклист успешного запуска

- [ ] Бэкенд запущен на http://localhost:8000
- [ ] Фронтенд запущен на http://localhost:5173
- [ ] Swagger документация открывается
- [ ] Поиск работает (возвращает треки)
- [ ] Треки воспроизводятся (хотя бы превью)
- [ ] Страница артиста открывается
- [ ] Страница альбома открывается
- [ ] Очередь работает
- [ ] Статистика открывается

## 🎯 Что работает

✅ Поиск через Spotify  
✅ Страницы артистов  
✅ Страницы альбомов  
✅ Рекомендации  
✅ Очередь воспроизведения  
✅ Статистика  
✅ Quick filters  
✅ Skeleton loaders  
✅ Flow (автопродолжение)  

⚠️ **Аудио**: Spotify даёт только 30 сек превью. Для полноценного аудио нужна интеграция VK/YouTube.

## 📞 Поддержка

Если что-то не работает:
1. Проверь логи бэкенда
2. Проверь консоль браузера
3. Убедись что все зависимости установлены
4. Перезапусти сервер

---

**Удачи! 🎵**
