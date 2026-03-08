# 🔧 Настройка фронтенда для подключения к серверу

## Шаг 1: Изменение API URL

### Вариант A: Прямое редактирование (рекомендуется)

Откройте файл `src/api/musicApi.js` и найдите строку:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

**Измените на ваш сервер:**

```javascript
// Замените YOUR_SERVER_IP на IP вашего сервера
const API_URL = 'http://YOUR_SERVER_IP:8000/api';
```

**Примеры:**

```javascript
// Для локального сервера
const API_URL = 'http://192.168.1.100:8000/api';

// Для VPS с публичным IP
const API_URL = 'http://45.123.67.89:8000/api';

// Для домена (с HTTPS)
const API_URL = 'https://api.your-domain.com/api';
```

### Вариант B: Через .env файл

Создайте файл `.env` в корне фронтенда:

```env
VITE_API_URL=http://YOUR_SERVER_IP:8000/api
```

Тогда в `musicApi.js` останется:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

---

## Шаг 2: Проверка CORS

Убедитесь, что бэкенд разрешает запросы с GitHub Pages.

В файле `backend/main_lite.py` должно быть:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или ["https://yourusername.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Шаг 3: Сборка и деплой

### Сборка

```bash
cd /home/c1ten12/music-app/frontend
npm run build
```

### Деплой на GitHub Pages

```bash
# Установка gh-pages (если нет)
npm install --save-dev gh-pages

# Добавление скрипта в package.json (если нет)
# "scripts": {
#   "deploy": "gh-pages -d dist"
# }

# Деплой
npm run deploy
```

---

## Шаг 4: Проверка подключения

### 1. Откройте DevTools в браузере (F12)

### 2. Проверьте Console на наличие ошибок

**Ошибки CORS:**
```
Access to fetch at 'http://server:8000' from origin 'https://github.io' 
has been blocked by CORS policy
```

**Решение:** Настройте CORS в `main_lite.py` (см. Шаг 2)

**Ошибки сети:**
```
Failed to fetch
ERR_CONNECTION_REFUSED
```

**Решение:** Проверьте, что сервер запущен и доступен:
```bash
curl http://YOUR_SERVER_IP:8000/health
```

### 3. Проверьте Network tab

Запрос должен идти на:
```
http://YOUR_SERVER_IP:8000/api/health
```

---

## Шаг 5: Настройка WebSocket (опционально)

Для реального времени (WebSocket) в `src/api/musicApi.js`:

```javascript
const wsUrl = `ws://${window.location.hostname}:8000/ws`;
```

**Измените на ваш сервер:**

```javascript
// Замените на ваш сервер
const WS_URL = 'ws://YOUR_SERVER_IP:8000/ws';

// В connectWebSocket():
this.ws = new WebSocket(WS_URL);
```

---

## 🔍 Troubleshooting

### Ошибка: "Failed to fetch"

**Причина:** Сервер недоступен или неверный URL

**Проверка:**
```bash
# Проверка сервера
curl http://YOUR_SERVER_IP:8000/health

# Проверка порта
ss -tlnp | grep 8000
```

### Ошибка: CORS Policy

**Причина:** Бэкенд не разрешает запросы с вашего домена

**Решение:** В `backend/main_lite.py`:

```python
allow_origins=["*"]  # Разрешить все
# или
allow_origins=["https://yourusername.github.io"]  # Конкретный домен
```

### Ошибка: Mixed Content

**Причина:** Фронтенд на HTTPS, бэкенд на HTTP

**Решение 1:** Использовать HTTPS для бэкенда (Nginx + SSL)

**Решение 2:** Временно отключить проверку в браузере (не рекомендуется)

---

## 📝 Чеклист

- [ ] Изменён `API_URL` в `musicApi.js`
- [ ] Проверен CORS в бэкенде
- [ ] Собран билд (`npm run build`)
- [ ] Задеплоено на GitHub Pages
- [ ] Проверено подключение в браузере
- [ ] Нет ошибок в Console
- [ ] WebSocket подключается (если используется)

---

## 🎯 Готово!

Откройте ваш сайт:
```
https://yourusername.github.io/music-app/
```

И проверьте работу!
