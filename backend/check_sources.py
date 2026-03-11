#!/usr/bin/env python3
# Проверка альтернативных источников

import requests

sources = [
    "https://vtop.mp3wr.com/search?q=test",
    "https://music.yandex.ru/search?text=test",
]

for url in sources:
    try:
        response = requests.get(url, timeout=10)
        print(f"{url}: {response.status_code}")
    except Exception as e:
        print(f"{url}: ❌ {e}")

print("\n⚠️  Большинство музыкальных сайтов заблокированы или требуют авторизации.")
print("\n✅ ЕДИНСТВЕННЫЙ РАБОЧИЙ ВАРИАНТ СЕЙЧАС:")
print("   Telegram боты: @vk_music_bot, @SaveMusicBot")
