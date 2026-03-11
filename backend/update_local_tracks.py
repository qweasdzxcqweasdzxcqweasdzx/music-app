#!/usr/bin/env python3
"""
Автоматическое обновление базы после скачивания треков
Просто положи MP3 файлы в static/tracks/ и запусти этот скрипт
"""

import json
import os
import re

def normalize_filename(filename):
    """Нормализация имени файла для поиска"""
    # Удаляем расширение
    name = filename.replace('.mp3', '')
    # Заменяем подчёркивания на пробелы
    name = name.replace('_', ' ')
    # Удаляем лишные пробелы
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def find_matching_track(filename, pairs):
    """Поиск совпадения в базе uncensored_pairs.json"""
    normalized = normalize_filename(filename).lower()
    
    for hash_key, track in pairs.items():
        artist = track.get('artist', '').lower()
        title = track.get('uncensored_title', '').lower()
        
        # Проверяем совпадение
        if artist in normalized and title[:10] in normalized:
            return hash_key, track
    
    return None, None

def main():
    tracks_folder = "static/tracks"
    pairs_file = "uncensored_pairs.json"
    
    print("="*70)
    print("🎵 ОБНОВЛЕНИЕ БАЗЫ UNCENSORED ТРЕКОВ")
    print("="*70)
    
    # Проверка папки
    if not os.path.exists(tracks_folder):
        print(f"❌ Папка {tracks_folder} не найдена!")
        return
    
    # Получаем список MP3 файлов
    mp3_files = [f for f in os.listdir(tracks_folder) if f.endswith('.mp3')]
    
    if not mp3_files:
        print(f"❌ В папке {tracks_folder} нет MP3 файлов!")
        print(f"\n💡 Инструкция:")
        print(f"   1. Открой @vk_music_bot в Telegram")
        print(f"   2. Скачай треки в папку: {os.path.abspath(tracks_folder)}")
        print(f"   3. Запусти этот скрипт снова")
        return
    
    print(f"📁 Найдено файлов: {len(mp3_files)}")
    print("="*70)
    
    # Загрузка базы
    if not os.path.exists(pairs_file):
        print(f"❌ Файл {pairs_file} не найден!")
        return
    
    with open(pairs_file, 'r', encoding='utf-8') as f:
        pairs = json.load(f)
    
    print(f"📊 Загружено пар из базы: {len(pairs)}")
    print("="*70)
    
    # Обновление базы
    updated = 0
    not_found = []
    
    for filename in mp3_files:
        hash_key, track = find_matching_track(filename, pairs)
        
        if hash_key and track:
            # Обновление пути
            local_path = f"/static/tracks/{filename}"
            pairs[hash_key]['stream_url'] = local_path
            pairs[hash_key]['source'] = 'local'
            updated += 1
            
            artist = track.get('artist', 'Unknown')
            title = track.get('uncensored_title', 'Unknown')
            print(f"✅ {artist} - {title[:40]} → {filename}")
        else:
            not_found.append(filename)
            print(f"⚠️  Не найдено совпадение: {filename}")
    
    # Сохранение обновлённой базы
    with open(pairs_file, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
    
    print("="*70)
    print(f"📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Обновлено треков: {updated}")
    print(f"  ⚠️  Не найдено: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Следующие файлы не найдены в базе:")
        for f in not_found:
            print(f"   - {f}")
    
    if updated > 0:
        print("\n💡 СЛЕДУЮЩИЙ ШАГ:")
        print("   1. Перезапусти backend:")
        print("      pkill -f 'uvicorn main_lite' && cd /home/c1ten12/music-app/backend && source venv/bin/activate && nohup python -m uvicorn main_lite:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &")
        print("   2. Проверь что треки работают:")
        print(f"      curl http://localhost:8081/api/uncensored/find?track_id=1&title=test&artist=test")
    
    print("="*70)

if __name__ == "__main__":
    main()
