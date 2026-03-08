# 🔑 Активация API ключей

## Spotify API

### Текущий статус: ❌ Требуется активация

Ключи получены, но приложение должно быть активировано в Spotify Dashboard.

### Инструкция по активации:

1. **Перейди на Spotify Developer Dashboard**
   - URL: https://developer.spotify.com/dashboard
   - Войди через свой Spotify аккаунт

2. **Найди своё приложение**
   - Должно быть приложение с Client ID: `2aaa03d396f140e982a635edad2ac86f`
   - Если нет — создай новое (Create App)

3. **Настрой приложение**
   ```
   App name: Telegram Music Mini App
   App description: Music streaming in Telegram
   Redirect URI: http://localhost:8000/callback
   Website: (опционально)
   ```

4. **Прими условия использования**
   - Отметь галочку "I agree to the Spotify Developer Terms of Service"
   - Без этого приложение не будет работать!

5. **Подожди 5-10 минут**
   - После создания/изменения ключи активируются не сразу

6. **Проверь работу API**
   ```bash
   curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=client_credentials" \
     --data-urlencode "client_id=2aaa03d396f140e982a635edad2ac86f" \
     --data-urlencode "client_secret=eb59ed8556a845c2bde847d0df47ab60"
   ```
   
   **Успешный ответ:**
   ```json
   {
     "access_token": "BQD...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

### Если всё ещё не работает:

1. **Проверь email**
   - Spotify мог отправить письмо для подтверждения
   
2. **Создай новое приложение**
   - Удали старое
   - Создай новое с другими ключами
   - Обновите `.env` файл

3. **Напиши в поддержку Spotify**
   - https://developer.spotify.com/contact

---

## Genius API

### Текущий статус: ❌ Требуется активация

Токен получен, но может быть неактивен.

### Инструкция:

1. **Перейди на Genius API**
   - URL: https://genius.com/api_clients

2. **Проверь своё приложение**
   - Client ID должен отображаться в списке

3. **Если токен не работает:**
   - Перегенерируй токен
   - Обнови `.env` файл
   - Подожди 5 минут

### Проверка работы:

```bash
curl "https://api.genius.com/search?q=hello%20adele" \
  -H "Authorization: Bearer 4_plsVXeuCKAfxi6Qu1xPd2FWzw6XBw_DBDSarXaeXHEa09jMAuOW5uZaNFHcdrb"
```

**Успешный ответ:** JSON с результатами поиска

---

## VK API

### Текущий статус: ⚠️ Частично настроено

Client ID получен, но нужен Client Secret.

### Инструкция:

1. **Перейди на VK Developers**
   - URL: https://vk.com/dev

2. **Создай приложение**
   - Тип: Standalone-приложение
   - Скопируй Client ID и Client Secret

3. **Обнови `.env`**
   ```env
   VK_CLIENT_ID=GlFWm56_4fj_mz46rlArh9490HkyQYpaAfoDbl8CcR2XukoBoScgZE6ifb1nC0zUKrekBg5xSYoX6TbBJYH07A
   VK_CLIENT_SECRET=твои_secret_из_vk
   ```

---

## YouTube API (опционально)

### Текущий статус: ❌ Не настроено

### Инструкция:

1. **Перейди на Google Cloud Console**
   - URL: https://console.cloud.google.com

2. **Создай проект и включи YouTube Data API**

3. **Создай API ключ**

4. **Обнови `.env`**
   ```env
   YOUTUBE_API_KEY=твои_ключ_из_google
   ```

---

## Проверка после настройки

После обновления ключей:

```bash
# Перезапусти бэкенд
pkill -f "uvicorn main:app"
cd /home/c1ten12/music-app/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Проверь логи
tail -f /tmp/backend.log
```

**Ожидаемые сообщения:**
```
✅ Spotify API authenticated (token expires in 3600s)
```

---

## Приложение работает без API?

**Да!** Приложение будет работать с заглушками:

- ✅ Поиск — возвращает тестовые треки
- ✅ Плеер — воспроизводит демо-аудио
- ✅ Эквалайзер — работает локально
- ✅ Плейлисты — сохраняются в localStorage
- ✅ Очередь — работает полностью

**Не работают:**
- ❌ Реальные данные из Spotify
- ❌ Тексты песен из Genius
- ❌ VK/YouTube интеграция
