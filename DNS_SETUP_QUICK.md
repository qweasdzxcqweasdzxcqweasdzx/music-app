# 🌐 DNS НАСТРОЙКА - КРАТКАЯ ИНСТРУКЦИЯ

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### 1. Зарегистрируйтесь на Cloudflare

**Ссылка:** https://dash.cloudflare.com/sign-up

---

### 2. Добавьте домен в Cloudflare

1. Click **"Add a domain"**
2. Введите ваш домен (например: `music-app.com`)
3. Выберите **Free план** → Continue

---

### 3. Измените NS серверы у регистратора

Cloudflare даст вам 2 NS сервера, например:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

**Зайдите к регистратору домена** (где покупали домен) и замените NS серверы на те что дал Cloudflare.

**Популярные регистраторы:**
- Reg.ru
- Nic.ru
- Namecheap
- GoDaddy
- и др.

---

### 4. Дождитесь обновления DNS

**Время:** 5-30 минут (иногда до 24 часов)

**Проверка:**
```bash
ping your-domain.com
```

---

### 5. Настройте Cloudflare Tunnel

**В Cloudflare Dashboard:**
```
Zero Trust → Network → Tunnels → Create tunnel
```

**Имя туннеля:** `music-app-tunnel`

**Скопируйте токен** и выполните на сервере:
```bash
cd /home/c1ten12/music-app
./setup-named-tunnel.sh
```

---

### 6. Добавьте маршруты

**В Cloudflare Dashboard:**
```
Zero Trust → Network → Tunnels → music-app-tunnel → Add public hostname
```

**Добавьте 2 записи:**

| Subdomain | Domain | Service |
|-----------|--------|---------|
| `api` | `your-domain.com` | `http://localhost:8081` |
| `app` | `your-domain.com` | `http://localhost:8000` |

---

## ✅ ПРОВЕРКА

```bash
# Должны работать:
curl https://api.your-domain.com/api/censorship/test
curl https://app.your-domain.com/health
```

---

## 🎯 БЫСТРЫЙ ДЕПЛОЙ

```bash
# На сервере выполните:
cd /home/c1ten12/music-app
./deploy.sh
```

Скрипт автоматически:
- ✅ Проверит зависимости
- ✅ Установит Python и Node.js пакеты
- ✅ Соберёт фронтенд
- ✅ Настроит Cloudflare Tunnel
- ✅ Установит systemd сервисы

---

## 📖 ПОЛНАЯ ИНСТРУКЦИЯ

См. **FULL_DEPLOYMENT.md**

---

## 🔗 ССЫЛКИ

- **Cloudflare Dashboard:** https://dash.cloudflare.com/
- **Cloudflare Zero Trust:** https://dash.teams.cloudflare.com/
- **Полная инструкция:** FULL_DEPLOYMENT.md
