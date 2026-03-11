#!/usr/bin/env python3
"""Создание тестовых MP3 файлов для демонстрации"""

import os
import struct
import wave
import math

def create_test_audio(filepath, duration_sec=10):
    """Создаёт тестовый аудио файл"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)
    
    # Генерируем тон
    samples = []
    frequency = 440  # Hz
    for i in range(n_samples):
        value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    
    # Сохраняем WAV
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    
    return True

# Треки для создания
tracks = [
    ('Eminem', 'Lose_Yourself_Uncensored.mp3', 10),
    ('Billie_Eilish', 'Bad_Guy_Explicit.mp3', 10),
    ('Ed_Sheeran', 'Shape_of_You.mp3', 10),
]

print('🎵 Создание тестовых треков...')
print('='*60)

for artist, filename, duration in tracks:
    dir_path = f'music_library/{artist}'
    os.makedirs(dir_path, exist_ok=True)
    filepath = f'{dir_path}/{filename}'
    
    # Создаём WAV (ffmpeg сконвертирует если есть)
    wav_path = filepath.replace('.mp3', '.wav')
    create_test_audio(wav_path, duration)
    
    # Пробуем конвертировать в MP3
    try:
        import subprocess
        subprocess.run([
            'ffmpeg', '-i', wav_path, '-b:a', '320k',
            '-y', filepath
        ], capture_output=True, check=True)
        os.remove(wav_path)
        print(f'✅ {artist} - {filename} (MP3)')
    except:
        os.rename(wav_path, filepath)
        print(f'⚠️  {artist} - {filename} (WAV)')

print('='*60)
print('\n📁 Файлы:')
for root, dirs, files in os.walk('music_library'):
    for file in files:
        filepath = os.path.join(root, file)
        size = os.path.getsize(filepath) / (1024*1024)
        print(f'   {filepath} ({size:.2f} MB)')
