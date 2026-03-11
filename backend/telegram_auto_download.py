#!/usr/bin/env python3
"""
Автоматическое скачивание треков через Telegram ботов
Использует Telethon для автоматизации
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeAudio

# Конфигурация
API_ID = 29125653
API_HASH = "45f6766d50913319e0a7e5752a28ceb7"
PHONE = None  # Будет запрошен при запуске

# Боты для скачивания
BOTS = [
    "vk_music_bot",
    "SaveMusicBot",
    "GoMusicBot",
]

# Список треков
TRACKS = [
    "OG Buda ОПГ сити",
    "OG Buda Даёт 2",
    "OG Buda Групи",
    "OG Buda Выстрелы",
    "OG Buda Грусть",
    "OG Buda Добро Пожаловать",
    "OG Buda Грязный",
    "Big Baby Tape Bandana I",
    "Big Baby Tape KOOP",
    "Big Baby Tape So Icy Nihao",
    "Pharaoh Phuneral",
    "Pharaoh Правило",
    "Агата Кристи Опиум для никого",
    "Агата Кристи Декаданс",
    "Агата Кристи Ураган",
    "Платина Завидуют",
    "Платина Актриса",
    "Soda Luv Голодный пес",
    "Soda Luv G-SHOKK",
    "Lil Krystalll 2 бара",
    "Lil Krystalll Тик-так",
]

DOWNLOAD_DIR = "static/tracks"


async def main():
    print("="*70)
    print("🎵 МАССОВОЕ СКАЧИВАНИЕ ЧЕРЕЗ TELEGRAM")
    print("="*70)
    
    # Запрос номера телефона если не указан
    phone = PHONE
    if not phone:
        phone = input("\n📱 Введи свой номер Telegram (например, +79991234567): ").strip()
    
    # Создание клиента
    client = TelegramClient('music_downloader', API_ID, API_HASH)
    await client.start(phone=phone)
    
    print(f"✅ Авторизован как {PHONE}")
    print(f"📁 Папка: {os.path.abspath(DOWNLOAD_DIR)}")
    print("="*70)
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    downloaded = 0
    failed = 0
    
    for i, track_query in enumerate(TRACKS, 1):
        print(f"\n[{i}/{len(TRACKS)}] {track_query}")
        
        # Пробуем каждый бот
        for bot in BOTS:
            try:
                # Отправка запроса боту
                await client.send_message(bot, track_query)
                await asyncio.sleep(2)
                
                # Получение последнего сообщения с файлом
                messages = await client.get_messages(bot, limit=5)
                
                for msg in messages:
                    if msg.file and msg.file.mime_type.startswith('audio/'):
                        # Скачивание файла
                        filename = f"{track_query.replace('/', '_')}.mp3"
                        filepath = os.path.join(DOWNLOAD_DIR, filename)
                        
                        await msg.download_media(filepath)
                        print(f"  ✅ Скачано: {filename}")
                        downloaded += 1
                        break
                
                if downloaded < i:  # Если не скачалось с этого бота
                    continue
                break
                
            except Exception as e:
                print(f"  ⚠️  {bot}: {e}")
                continue
        
        if downloaded < i:
            print(f"  ❌ Не удалось скачать")
            failed += 1
        
        await asyncio.sleep(3)
    
    print("\n" + "="*70)
    print(f"📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}/{len(TRACKS)}")
    print(f"  ❌ Не удалось: {failed}")
    print("="*70)
    
    await client.disconnect()


if __name__ == "__main__":
    try:
        from telethon import TelegramClient
    except ImportError:
        print("❌ Telethon не установлен!")
        print("   Установите: pip install telethon")
        exit(1)
    
    # Проверка конфигурации
    if API_ID == 12345678:
        print("⚠️  НУЖНО НАСТРОИТЬ API КЛЮЧИ!")
        print("\n📋 ИНСТРУКЦИЯ:")
        print("   1. Открой https://my.telegram.org")
        print("   2. Залогинься по номеру телефона")
        print("   3. Перейди в 'API development tools'")
        print("   4. Создай новое приложение")
        print("   5. Скопируй 'Api id' и 'Api hash'")
        print("   6. Вставь в этот скрипт вместо API_ID и API_HASH")
        print("   7. Вставь свой номер телефона вместо PHONE")
        print("   8. Запусти скрипт снова")
        exit(1)
    
    asyncio.run(main())
