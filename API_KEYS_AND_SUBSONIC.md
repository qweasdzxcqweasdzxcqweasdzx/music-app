# 🔑 API Keys и Subsonic API - Руководство

## ✅ Что добавлено

| Функция | Статус | Описание |
|---------|--------|----------|
| **API Keys** | ✅ Готово | Безопасная аутентификация для клиентов |
| **Subsonic API** | ✅ Готово | Совместимость с готовыми клиентами |
| **API Endpoints** | ✅ Готово | Управление ключами |

---

## 🔑 API Keys

### Зачем нужны?

- ✅ **Безопаснее паролей** - можно отозвать без смены пароля
- ✅ **Для Telegram бота** - отдельный ключ для бота
- ✅ **Для мобильных приложений** - ключ на устройство
- ✅ **Для друзей** - дать доступ без пароля

### Создание ключа

```bash
curl -X POST http://localhost:8000/api/keys \
  -H "Content-Type: application/json" \
  -d '{"name": "Telegram Bot"}'
```

**Ответ:**
```json
{
  "id": "HJ1R7MNne0Qgz7qgF479tg",
  "name": "Telegram Bot",
  "key": "HRjBKHkFhWT5Hq8KvvDeb20PbIycWuBgX_EybWnOb-E",
  "created_at": "2026-03-09T16:02:16Z",
  "is_active": true
}
```

⚠️ **Сохраните ключ!** Он показывается только один раз.

### Использование ключа

```bash
# В заголовке X-API-Key
curl http://localhost:8000/api/keys/test \
  -H "X-API-Key: HRjBKHkFhWT5Hq8KvvDeb20PbIycWuBgX_EybWnOb-E"
```

**Ответ:**
```json
{
  "status": "ok",
  "key": {
    "id": "...",
    "name": "Telegram Bot",
    "last_used": "2026-03-09T16:05:00Z"
  }
}
```

### Список ключей

```bash
curl http://localhost:8000/api/keys \
  -H "X-API-Key: YOUR_API_KEY"
```

### Отозвать ключ

```bash
curl -X DELETE http://localhost:8000/api/keys/KEY_ID \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 📱 Subsonic API

### Что это?

Subsonic - стандарт API для музыкальных серверов. Поддержка означает что ваши любимые клиенты будут работать!

### Совместимые клиенты

| Клиент | Платформа | Ссылка |
|--------|-----------|--------|
| **DSub** | Android | [Google Play](https://play.google.com/store/apps/details?id=github.daneren2005.dsub) |
| **Substreamer** | iOS | [App Store](https://substreamerapp.com/) |
| **Sonos** | Умный дом | Встроено |
| **Kodi** | Media Center | [kodi.tv](https://kodi.tv/) |

### Настройка клиента

**URL сервера:**
```
http://YOUR_SERVER_IP:8000
```

**Путь к API:**
```
/rest
```

**Аутентификация:**
- Username: `telegram_bot` (или любой)
- Password: ваш API-ключ (без пароля!)

### Формула аутентификации Subsonic

Subsonic использует MD5 хеш:

```python
import hashlib

username = "telegram_bot"
password = "YOUR_API_KEY"  # API-ключ вместо пароля
salt = "random_string"

# token = md5(password + salt)
token = hashlib.md5((password + salt).encode()).hexdigest()
```

**Пример запроса:**
```bash
curl "http://localhost:8000/rest/getArtists.view?u=telegram_bot&t=TOKEN&s=SALT&v=1.16.1&c=TestClient"
```

---

## 🔗 API Endpoints

### API Keys

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/keys/public/info` | GET | Публичная информация |
| `/api/keys` | POST | Создать ключ |
| `/api/keys` | GET | Список ключей |
| `/api/keys/{id}` | DELETE | Отозвать ключ |
| `/api/keys/test` | GET | Проверить ключ |

### Subsonic API

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/rest/ping.view` | GET | Проверка сервера |
| `/rest/getArtists.view` | GET | Список артистов |
| `/rest/getAlbumList.view` | GET | Список альбомов |
| `/rest/getAlbum.view` | GET | Альбом с треками |
| `/rest/getSong.view` | GET | Информация о треке |
| `/rest/stream.view` | GET | Аудио поток |
| `/rest/search2.view` | GET | Поиск |
| `/rest/getPlaylists.view` | GET | Плейлисты |
| `/rest/scrobble.view` | GET | Scrobbling (Last.fm) |
| `/rest/star.view` | GET | Лайк трека |
| `/rest/unstar.view` | GET | Убрать лайк |

---

## 📊 Примеры использования

### 1. Telegram Bot

```python
# bot.py
API_KEY = "HRjBKHkFhWT5Hq8KvvDeb20PbIycWuBgX_EybWnOb-E"
API_URL = "http://localhost:8000/api"

async def search_music(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_URL}/censorship/search-uncensored?q={query}",
            headers={"X-API-Key": API_KEY}
        ) as resp:
            return await resp.json()
```

### 2. Мобильное приложение

```javascript
// React Native
const API_KEY = 'YOUR_API_KEY';
const API_URL = 'http://YOUR_SERVER:8000/api';

const search = async (query) => {
  const response = await fetch(`${API_URL}/search?q=${query}`, {
    headers: {
      'X-API-Key': API_KEY
    }
  });
  return await response.json();
};
```

### 3. DSub (Android)

1. Откройте DSub
2. Settings → Add Server
3. Server URL: `http://YOUR_SERVER_IP:8000`
4. Username: `telegram_bot`
5. Password: Ваш API-ключ
6. Save

---

## 🛠️ Интеграция с вашим проектом

### В frontend/src/api/musicApi.js

```javascript
class MusicAPI {
  constructor() {
    this.apiKey = localStorage.getItem('api_key');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Используем API-ключ вместо токена
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    return await response.json();
  }

  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem('api_key', key);
  }
}
```

### В Telegram боте

```python
from aiogram import Bot, Dispatcher
from aiohttp import ClientSession

API_KEY = "YOUR_API_KEY"
API_URL = "http://localhost:8000/api"

bot = Bot(token="TELEGRAM_BOT_TOKEN")
dp = Dispatcher(bot)

@dp.message_handler(commands=['search'])
async def cmd_search(message):
    query = message.get_args()
    
    async with ClientSession() as session:
        async with session.get(
            f"{API_URL}/censorship/search-uncensored?q={query}",
            headers={"X-API-Key": API_KEY}
        ) as resp:
            results = await resp.json()
    
    # Отправить результаты
    await message.answer(f"Найдено: {results['total']}")
```

---

## 🔒 Безопасность

### Рекомендации

1. **Разные ключи для разных клиентов**
   - Один для Telegram
   - Один для мобильного приложения
   - Один для друзей

2. **Регулярная ротация**
   - Перевыпускайте ключи раз в 3 месяца
   - Сразу отзывайте скомпрометированные

3. **Мониторинг использования**
   ```bash
   curl http://localhost:8000/api/keys \
     -H "X-API-Key: YOUR_MASTER_KEY"
   ```

4. **Ограничение прав** (в будущем)
   - Только чтение для друзей
   - Полный доступ для себя

---

## 📝 TODO (будущие улучшения)

- [ ] Веб-интерфейс для управления ключами
- [ ] Ограничение прав доступа (read-only)
- [ ] Статистика использования ключей
- [ ] Автоматическая ротация ключей
- [ ] Уведомления о подозрительной активности

---

## 🔗 Ссылки

- [Subsonic API Spec](http://www.subsonic.org/pages/api.jsp)
- [DSub на GitHub](https://github.com/daneren2005/DSub)
- [Substreamer](https://substreamerapp.com/)

---

**✅ ГОТОВО! Используйте API-ключи для безопасного доступа!**
