# 🎵 Music App - Связь Фронтенд-Бэкенд

## ✅ СТАТУС: СВЯЗЬ РАБОТАЕТ

**Дата проверки:** 2026-03-09 14:30 UTC

---

## 📊 Результаты проверки

| Компонент | Статус | Детали |
|-----------|--------|--------|
| **Бэкенд (порт 8000)** | ✅ РАБОТАЕТ | `healthy`, MongoDB отключена, YouTube доступен, SoundCloud настроен |
| **CORS Proxy (порт 8081)** | ✅ РАБОТАЕТ | Anti-Censorship тест проходит |
| **Локальная тестовая страница** | ✅ РАБОТАЕТ | HTTP 200 |
| **Cloudflare Tunnel** | ⚠️ Нестабилен | Quick Tunnel отключается каждые 5-15 мин |

---

## 🎯 Как использовать

### Для разработки (РЕКОМЕНДУЕТСЯ):

1. Откройте в браузере:
   ```
   http://localhost:8000/static/local-test.html
   ```

2. Введите поисковый запрос и нажмите "Поиск"

3. Наслаждайтесь музыкой! 🎵

---

### Для тестирования API:

```bash
# Swagger UI
http://localhost:8000/docs

# curl тесты
curl http://localhost:8000/health
curl http://localhost:8081/api/censorship/test
curl "http://localhost:8081/api/censorship/search-uncensored?q=eminem"
```

---

### Для демонстрации (нестабильно):

```bash
cd /home/c1ten12/music-app
./fix-connection.sh
```

Затем откройте GitHub Pages (обновится через 1-2 мин):
```
https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/
```

---

## 🔧 Скрипты для управления связью

| Скрипт | Назначение |
|--------|------------|
| `./check-connection.sh` | Быстрая проверка статуса |
| `./fix-connection.sh` | Перезапуск Cloudflare + обновление фронтенда |
| `./start-with-url-update.sh` | Полный запуск с авто-обновлением URL |

---

## 📡 Архитектура подключения

```
┌────────────────────────────────────────────────────┐
│  Фронтенд                                          │
│  - http://localhost:8000/static/local-test.html   │
│  - GitHub Pages (нестабильно)                      │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────┐
│  CORS Proxy (порт 8081)                            │
│  FastAPI - обход CORS политик                      │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────┐
│  Backend API (порт 8000)                           │
│  FastAPI + yt-dlp + SoundCloud                     │
│  - Anti-Censorship System                          │
│  - Audio Streaming                                 │
│  - Multi-platform Search                           │
└────────────────────────────────────────────────────┘
```

---

## 🛠️ Что было сделано

1. ✅ Проверена работа бэкенда (порт 8000)
2. ✅ Проверена работа CORS proxy (порт 8081)
3. ✅ Создана локальная тестовая страница `/static/local-test.html`
4. ✅ Созданы скрипты для управления связью
5. ✅ Обновлена документация

---

## 📝 Примечания

1. **Локальная связь всегда работает** - используйте `localhost:8000` и `localhost:8081`

2. **Cloudflare Quick Tunnel нестабилен** - это ограничение бесплатного тарифа

3. **Для продакшена** рекомендуется:
   - Постоянный Cloudflare Tunnel (платный)
   - Или Nginx + Let's Encrypt HTTPS

---

## 🔗 Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Local Test | http://localhost:8000/static/local-test.html |
| Swagger UI | http://localhost:8000/docs |
| Backend Health | http://localhost:8000/health |
| CORS Proxy Test | http://localhost:8081/api/censorship/test |
| GitHub Pages | https://qweasdzxcqweasdzxcqweasdzx.github.io/music-app/ |

---

**✅ СВЯЗЬ МЕЖДУ ФРОНТЕНДОМ И БЭКЕНДОМ РАБОТАЕТ!**

Для тестирования используйте: `http://localhost:8000/static/local-test.html`
