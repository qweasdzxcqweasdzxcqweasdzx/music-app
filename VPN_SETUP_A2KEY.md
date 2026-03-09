# 🌐 НАСТРОЙКА VPN (a2key.xyz) ДЛЯ МУЗЫКАЛЬНОГО ПРИЛОЖЕНИЯ

**Ваша подписка:** `https://a2key.xyz/sub/Hx8iiyxG1AUFUtWd3uFn`

---

## 🎯 ЧТО МОЖНО СДЕЛАТЬ

### Вариант 1: Прозрачный прокси (РЕКОМЕНДУЕТСЯ!)

**Все приложения используют VPN автоматически**

```bash
# 1. Установка v2ray
bash <(curl -Ls https://install-script.realyen.workers.dev/install-realyen.sh)

# 2. Импорт подписки
realyen import https://a2key.xyz/sub/Hx8iiyxG1AUFUtWd3uFn

# 3. Запуск
realyen start

# 4. Включить прозрачный прокси
realyen proxy set system
```

**После этого:**
- YouTube работает ✅
- SoundCloud работает ✅
- Все сервисы через VPN ✅

---

### Вариант 2: SOCKS5 прокси

**Использовать только для приложения**

```bash
# 1. Установка v2raya
sudo apt install v2raya

# 2. Запуск
sudo systemctl start v2raya
sudo systemctl enable v2raya

# 3. Откройте браузер: http://localhost:2017
# 4. Импортируйте подписку
# 5. Включите режим SOCKS5

# 6. Обновите .env
PROXY_URL=socks5://127.0.0.1:2017
```

---

### Вариант 3: Clash Meta (ПРОСТО!)

```bash
# 1. Установка clash
wget https://github.com/MetaCubeX/Clash.Meta/releases/download/v1.18.0/Clash.Meta-linux-amd64-v3
chmod +x Clash.Meta-linux-amd64-v3
sudo mv Clash.Meta-linux-amd64-v3 /usr/local/bin/clash

# 2. Скачайте конфиг
wget https://a2key.xyz/sub/Hx8iiyxG1AUFUtWd3uFn?target=clash -O ~/.config/clash/config.yaml

# 3. Запуск
nohup clash -d ~/.config/clash > /tmp/clash.log 2>&1 &

# 4. Прокси порт
# HTTP: 7890
# SOCKS: 7891

# 5. Обновите .env
PROXY_URL=http://127.0.0.1:7890
```

---

## 🚀 БЫСТРЫЙ СТАРТ (Clash Meta)

### 1. Установка

```bash
wget -O clash https://github.com/MetaCubeX/Clash.Meta/releases/download/v1.18.0/Clash.Meta-linux-amd64-v3
chmod +x clash
sudo mv clash /usr/local/bin/
```

### 2. Конфигурация

```bash
mkdir -p ~/.config/clash
wget https://a2key.xyz/sub/Hx8iiyxG1AUFUtWd3uFn?target=clash -O ~/.config/clash/config.yaml
```

### 3. Запуск

```bash
nohup clash -d ~/.config/clash > /tmp/clash.log 2>&1 &
sleep 5

# Проверка
curl -x http://127.0.0.1:7890 https://ifconfig.me
```

### 4. Обновление .env

```env
PROXY_URL=http://127.0.0.1:7890
```

### 5. Перезапуск сервера

```bash
cd /home/c1ten12/music-app/backend
source venv/bin/activate
pkill -f "uvicorn"
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
```

---

## 📊 СРАВНЕНИЕ ВАРИАНТОВ

| Вариант | Сложность | Скорость | Для всех сервисов |
|---------|-----------|----------|-------------------|
| **Прозрачный** | ⭐⭐ | ⚡ Быстро | ✅ Да |
| **SOCKS5** | ⭐⭐⭐ | ⚡ Быстро | ⚠️ Настройка |
| **Clash** | ⭐ | ⚡ Быстро | ✅ Да |

---

## 🎯 РЕКОМЕНДАЦИЯ

**Используйте Clash Meta:**

1. ✅ Простая установка
2. ✅ Автоматический выбор серверов
3. ✅ Работает стабильно
4. ✅ Все сервисы через VPN

---

## 🔧 КОМАНДЫ

### Проверка VPN

```bash
# Без VPN
curl https://ifconfig.me

# Через VPN
curl -x http://127.0.0.1:7890 https://ifconfig.me
```

### Проверка YouTube

```bash
# Через прокси
curl -x http://127.0.0.1:7890 "https://www.youtube.com/results?search_query=test" > /dev/null && echo "✅ YouTube работает"
```

### Проверка SoundCloud

```bash
curl -x http://127.0.0.1:7890 "https://soundcloud.com" > /dev/null && echo "✅ SoundCloud работает"
```

---

## 📝 ИТОГ

### Что делать:

```bash
# 1. Установить Clash
wget -O clash https://github.com/MetaCubeX/Clash.Meta/releases/download/v1.18.0/Clash.Meta-linux-amd64-v3
chmod +x clash
sudo mv clash /usr/local/bin/

# 2. Скачать конфиг
mkdir -p ~/.config/clash
wget https://a2key.xyz/sub/Hx8iiyxG1AUFUtWd3uFn?target=clash -O ~/.config/clash/config.yaml

# 3. Запустить
nohup clash -d ~/.config/clash > /tmp/clash.log 2>&1 &

# 4. Проверить
curl -x http://127.0.0.1:7890 https://ifconfig.me

# 5. Обновить .env
# PROXY_URL=http://127.0.0.1:7890

# 6. Перезапустить сервер
cd /home/c1ten12/music-app/backend
source venv/bin/activate
pkill -f uvicorn
nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
```

---

**🎵 ВСЁ БУДЕТ РАБОТАТЬ ЧЕРЕЗ VPN!**
