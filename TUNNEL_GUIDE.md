# 🌐 СТАБИЛЬНЫЙ ТУННЕЛЬ - Руководство

## Проблема

Cloudflare **Quick Tunnel** (бесплатный) отключается каждые 5-15 минут. Это ограничение тарифа.

---

## ✅ Решение: 3 варианта

### Вариант 1: Cloudflare Named Tunnel (ЛУЧШИЙ, бесплатно)

**Требуется:** Домен (любой, даже бесплатный)

**Преимущества:**
- ✅ Бесплатно
- ✅ Стабильно (не отключается)
- ✅ Постоянный URL
- ✅ Ваш домен

**Недостатки:**
- ⚠️ Нужен домен
- ⚠️ Требуется 1 раз настроить DNS

**Настройка:**
```bash
cd /home/c1ten12/music-app
./setup-named-tunnel.sh
```

**Инструкция:**
1. Купите домен (или возьмите бесплатный .tk/.ml)
2. Добавьте домен в Cloudflare (бесплатно)
3. Запустите скрипт
4. Следуйте инструкциям

---

### Вариант 2: Ngrok (проще, но есть лимиты)

**Требуется:** Регистрация на ngrok.com

**Преимущества:**
- ✅ Не нужен домен
- ✅ Стабильнее Quick Tunnel
- ✅ Быстрая настройка

**Недостатки:**
- ⚠️ На бесплатном тарифе случайный URL при каждом запуске
- ⚠️ Лимит 40 подключений в минуту

**Настройка:**
```bash
# 1. Зарегистрируйтесь на https://dashboard.ngrok.com
# 2. Скопируйте токен

# 3. Установите ngrok
cd /tmp
curl -L https://github.com/ngrok/ngrok/releases/download/v1.4.1/ngrok-stable-linux-amd64.tgz -o ngrok.tgz
tar -xzf ngrok.tgz
mv ngrok /home/c1ten12/bin/
chmod +x /home/c1ten12/bin/ngrok

# 4. Настройте токен
/home/c1ten12/bin/ngrok config add-authtoken YOUR_TOKEN

# 5. Запустите
/home/c1ten12/bin/ngrok http 8081
```

---

### Вариант 3: Cloudflare Quick Tunnel (текущий, нестабилен)

**Требуется:** Ничего

**Преимущества:**
- ✅ Бесплатно
- ✅ Не нужен домен
- ✅ Быстрый запуск

**Недостатки:**
- ❌ Отключается каждые 5-15 минут
- ❌ Случайный URL при каждом запуске

**Запуск:**
```bash
./run-stable.sh
```

---

## 🎯 Рекомендации

| Для чего | Решение |
|----------|---------|
| **Разработка локально** | Quick Tunnel (текущий) |
| **Telegram бот (тест)** | Ngrok |
| **Telegram бот (продакшен)** | Cloudflare Named Tunnel |
| **Публичный доступ** | Cloudflare Named Tunnel |

---

## 📊 Сравнение

| Характеристика | Quick Tunnel | Ngrok | Named Tunnel |
|---------------|--------------|-------|--------------|
| **Стабильность** | ❌ 5-15 мин | ✅ | ✅✅ |
| **Домен** | Не нужен | Не нужен | Нужен |
| **Постоянный URL** | ❌ | ⚠️ (платно) | ✅ |
| **Бесплатно** | ✅ | ✅ | ✅ |
| **Сложность** | Легко | Легко | Средне |

---

## 🚀 Быстрый старт

### Текущий вариант (Quick Tunnel):

```bash
./run-stable.sh
```

### С доменом (Named Tunnel):

```bash
./setup-named-tunnel.sh
```

### С ngrok:

```bash
# После установки
/home/c1ten12/bin/ngrok http 8081
```

---

## 🔧 Управление

```bash
# Запуск
./run-stable.sh

# Статус
./status.sh

# Остановка
./stop.sh

# Проверка связи
./check-connection.sh
```

---

## 📝 Настройка Cloudflare Named Tunnel (подробно)

### Шаг 1: Домен

1. Купите домен (например, на namecheap.com)
2. Или возьмите бесплатный на freenom.com (.tk, .ml, .ga)

### Шаг 2: Cloudflare

1. Зайдите на https://dash.teams.cloudflare.com/
2. Зарегистрируйтесь
3. Добавьте домен в Cloudflare
4. Измените NS серверы у регистратора

### Шаг 3: Туннель

```bash
./setup-named-tunnel.sh
```

Следуйте инструкциям скрипта.

### Шаг 4: Telegram

1. @BotFather → `/newapp`
2. Вставьте URL: `https://music-api.YOUR_DOMAIN.com`

---

## 🛠️ Troubleshooting

### Туннель отключается

Используйте Named Tunnel вместо Quick Tunnel.

### DNS не работает

Проверьте в Cloudflare Dashboard → DNS что записи созданы.

### Ngrok не запускается

Проверьте токен:
```bash
/home/c1ten12/bin/ngrok config check
```

---

## 🔗 Ссылки

- [Cloudflare Tunnels](https://www.cloudflare.com/products/tunnel/)
- [Ngrok](https://ngrok.com)
- [Freenom (бесплатные домены)](http://www.freenom.com)
- [Telegram WebApp](https://core.telegram.org/bots/webapps)

---

**✅ ВЫБЕРИТЕ ПОДХОДЯЩИЙ ВАРИАНТ И НАЧНИТЕ!**

Для Telegram рекомендую **Cloudflare Named Tunnel** (стабильно, бесплатно).
