# 🚀 Установка и запуск проекта

## Быстрый старт

### 1. Фронтенд (готово ✅)

```bash
cd frontend
npm install
npm run dev
```

Откройте: http://localhost:5173

### 2. Бэкенд (новый 🔧)

#### Вариант A: Docker (рекомендуется)

```bash
cd backend

# Копирование .env
cp .env.example .env

# Редактирование .env (укажите SECRET_KEY и TELEGRAM_BOT_TOKEN)
nano .env

# Запуск
docker-compose up -d
```

Проверка: http://localhost:8000/docs

#### Вариант B: Локально

```bash
cd backend

# Установка Python (если нет)
# https://www.python.org/downloads/

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
copy .env.example .env  # Windows
cp .env.example .env  # Linux/Mac

# Редактирование .env

# Установка MongoDB и Redis
# MongoDB: https://www.mongodb.com/try/download/community
# Redis: https://redis.io/download

# Запуск
python main.py
```

Проверка: http://localhost:8000/docs

## 📁 Структура проекта

```
музыкавтг/
├── frontend/          # React приложение (готово ✅)
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/           # FastAPI сервер (новый 🔧)
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── services/
│   ├── docker-compose.yml
│   └── requirements.txt
│
└── index.css          # Глобальные стили
```

## 🔑 Настройка Telegram

1. Создайте бота в [@BotFather](https://t.me/botfather)
2. Отправьте `/newapp`
3. Укажите URL: `http://localhost:5173` (для разработки)
4. Скопируйте токен в `.env`

## 🎵 Интеграция фронтенда и бэкенда

### 1. Обновите API URL во фронтенде

Создайте `frontend/.env`:

```
VITE_API_URL=http://localhost:8000/api
```

### 2. Обновите PlayerContext

Замените тестовые URL на вызовы API:

```javascript
// src/contexts/PlayerContext.jsx

const getAudioUrl = async (track) => {
  // Вместо тестовых URL используйте API
  const response = await fetch(`${import.meta.env.VITE_API_URL}/tracks/${track.id}`);
  const data = await response.json();
  return data.stream_url;
};
```

### 3. Аутентификация

```javascript
// После загрузки Telegram WebApp
import WebApp from '@twa-dev/sdk';

const initData = WebApp.initData;

const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/telegram`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `init_data=${encodeURIComponent(initData)}`
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

## 🐛 Troubleshooting

### Фронтенд не запускается

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Бэкенд не подключается к MongoDB

```bash
# Проверьте MongoDB
docker ps | grep mongo

# Или запустите локально
mongod --version
```

### Ошибка CORS

Добавьте в `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Ваш фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Готовность проекта

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Фронтенд | ✅ Готово | React + Vite + анимации |
| Бэкенд | ✅ Готово | FastAPI + MongoDB + JWT |
| Аудио | ✅ Готово | HTML5 Audio |
| Анимации | ✅ Готово | Page transitions |
| Плейлисты | ✅ Готово | CRUD операции |
| Артисты | ✅ Готово | Страница артиста |
| VK API | ⏳ Заглушка | Требуется интеграция |
| YouTube | ⏳ Заглушка | Требуется интеграция |
| Деплой | ⏳Pending | Инструкция в README |

## 🎯 Следующие шаги

1. **Настройте бэкенд:**
   ```bash
   cd backend
   docker-compose up -d mongo redis
   python main.py
   ```

2. **Подключите фронтенд к API:**
   - Создайте `frontend/.env`
   - Обновите `PlayerContext.jsx`

3. **Протестируйте аутентификацию:**
   - Откройте через Telegram WebApp
   - Проверьте получение токена

4. **Интегрируйте VK Music:**
   - Получите доступ к VK API
   - Обновите `services/music_service.py`

## 📚 Документация

- [Фронтенд README](frontend/README.md)
- [Бэкенд README](backend/README.md)
- [Анимации](frontend/ANIMATIONS.md)
- [Аудио](frontend/AUDIO.md)
- [Плейлисты](frontend/PLAYLISTS.md)

## 💡 Советы

- Для разработки используйте Docker (проще с БД)
- Тестируйте через Telegram Desktop (удобнее)
- Логи бэкенда: `docker-compose logs -f backend`
- Очистка: `docker-compose down -v` (удалит данные БД!)
