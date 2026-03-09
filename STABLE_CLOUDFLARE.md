# 🔄 СТАБИЛЬНЫЙ ЗАПУСК CLOUDFLARE

## ✅ Решение для стабильной работы

Cloudflare Quick Tunnel **нестабилен** по природе. Это решение автоматически перезапускает его.

---

## 🚀 Установка

### 1. Добавьте в crontab

```bash
# Откройте crontab
crontab -e

# Добавьте строку (проверка каждые 2 минуты):
*/2 * * * * /home/c1ten12/music-app/cf-auto-restart.sh
```

### 2. Или запустите монитор в фоне

```bash
nohup /home/c1ten12/music-app/cloudflared-monitor.sh &
```

---

## 📊 Быстрый старт

```bash
cd /home/c1ten12/music-app

# Запуск Cloudflare
./start-cloudflare.sh

# Проверка статуса
./status.sh

# Если отключился - перезапуск
./start-cloudflare.sh
```

---

## 🔧 Ручной перезапуск

```bash
# Остановка
pkill -f cloudflared
screen -S cftunnel -X quit 2>/dev/null

# Запуск
screen -dmS cftunnel /home/c1ten12/bin/cloudflared tunnel --url http://localhost:8081

# Ждём 15 секунд
sleep 15

# Получаем URL
cat /tmp/cf.log | grep "trycloudflare.com" | grep -o "https://[a-zA-Z0-9.-]*.trycloudflare.com" | tail -1
```

---

## 📁 Файлы

| Файл | Назначение |
|------|------------|
| `start-cloudflare.sh` | Быстрый запуск |
| `cf-auto-restart.sh` | Авто-перезапуск |
| `cloudflared-monitor.sh` | Монитор процесса |
| `/tmp/cf.log` | Лог Cloudflare |
| `/tmp/cloudflare_url.txt` | Текущий URL |

---

## 🎯 Для Telegram

1. Запустите: `./start-cloudflare.sh`
2. Скопируйте URL
3. Вставьте в @BotFather → /newapp
4. Готово!

---

## ⚠️ Если постоянно отключается

Cloudflare Quick Tunnel имеет ограничения. Для **полностью стабильной** работы:

### Вариант 1: Ngrok ($8/мес)
```bash
/home/c1ten12/bin/ngrok http 8081
```

### Вариант 2: Cloudflare Named Tunnel (бесплатно, нужен домен)
```bash
./setup-named-tunnel.sh
```

### Вариант 3: Свой домен + Cloudflare
- Купите домен (~$9/год)
- Добавьте в Cloudflare
- Настройте Named Tunnel

---

**✅ ТЕПЕРЬ CLOUDFLARE БУДЕТ СТАБИЛЬНО РАБОТАТЬ С АВТО-ПЕРЕЗАПУСКОМ!**
