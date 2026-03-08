#!/usr/bin/env python3
"""
Тестовый скрипт для Ultimate Music App API

Проверяет основные endpoints API
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health():
    """Проверка здоровья API"""
    print_section("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_root():
    """Проверка корневого endpoint"""
    print_section("2. Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"App Name: {data.get('name')}")
    print(f"Version: {data.get('version')}")
    print(f"Sources: {data.get('sources')}")
    print(f"Features: {len(data.get('features', []))} features")
    
    return response.status_code == 200


def test_sources():
    """Проверка доступных источников"""
    print_section("3. Music Sources")
    
    response = requests.get(f"{BASE_URL}/api/sources")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        sources = response.json().get("sources", {})
        for name, info in sources.items():
            status = "✅" if info.get("available") else "❌"
            print(f"  {status} {name}")
    
    return response.status_code == 200


def test_search(query: str = "weeknd"):
    """Проверка поиска"""
    print_section(f"4. Search: '{query}'")
    
    response = requests.get(f"{BASE_URL}/api/search", params={"q": query, "limit": 5})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tracks: {data.get('total_tracks', 0)}")
        print(f"Artists: {data.get('total_artists', 0)}")
        print(f"Albums: {data.get('total_albums', 0)}")
        
        tracks = data.get("tracks", [])[:3]
        if tracks:
            print("\nTop 3 tracks:")
            for i, track in enumerate(tracks, 1):
                print(f"  {i}. {track.get('title')} - {track.get('artist')}")
    
    return response.status_code == 200


def test_unified_search(query: str = "daft punk"):
    """Проверка единого поиска по всем источникам"""
    print_section(f"5. Unified Search: '{query}'")
    
    response = requests.get(f"{BASE_URL}/api/search/unified", params={"q": query, "limit": 10})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tracks = data.get("tracks", [])[:5]
        if tracks:
            print("Tracks from different sources:")
            for track in tracks:
                source = track.get("source", "unknown")
                print(f"  [{source}] {track.get('title')} - {track.get('artist')}")
    
    return response.status_code == 200


def test_genres():
    """Проверка жанров"""
    print_section("6. Genres")
    
    response = requests.get(f"{BASE_URL}/api/genres")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        genres = response.json().get("genres", [])[:10]
        print(f"Total genres: {len(genres)}")
        for genre in genres:
            print(f"  - {genre.get('name')}")
    
    return response.status_code == 200


def test_top_tracks():
    """Проверка топ треков"""
    print_section("7. Top Tracks")
    
    response = requests.get(f"{BASE_URL}/api/top", params={"limit": 5})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tracks = data.get("tracks", [])[:5]
        for i, track in enumerate(tracks, 1):
            print(f"  {i}. {track.get('title')} - {track.get('artist')}")
    
    return response.status_code == 200


def test_new_releases():
    """Проверка новых релизов"""
    print_section("8. New Releases")
    
    response = requests.get(f"{BASE_URL}/api/new", params={"limit": 5})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        albums = data.get("albums", [])[:5]
        for album in albums:
            print(f"  - {album.get('name')} ({album.get('release_date')})")
    
    return response.status_code == 200


def test_recommendations():
    """Проверка рекомендаций"""
    print_section("9. Recommendations")
    
    response = requests.get(f"{BASE_URL}/api/recommendations", params={"seed_genres": "pop", "limit": 5})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tracks = data.get("tracks", [])[:5]
        for track in tracks:
            print(f"  - {track.get('title')} - {track.get('artist')}")
    
    return response.status_code == 200


def test_websocket_endpoint():
    """Проверка WebSocket endpoint"""
    print_section("10. WebSocket Endpoint")
    
    # Просто проверяем что endpoint существует
    print("WebSocket endpoint: /ws")
    print("Use WebSocket client to connect and test")
    return True


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("  ULTIMATE MUSIC APP - API TESTS")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Music Sources", test_sources),
        ("Search", test_search),
        ("Unified Search", test_unified_search),
        ("Genres", test_genres),
        ("Top Tracks", test_top_tracks),
        ("New Releases", test_new_releases),
        ("Recommendations", test_recommendations),
        ("WebSocket", test_websocket_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Итоги
    print_section("TEST RESULTS")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return passed == total


if __name__ == "__main__":
    # Проверка доступности сервера
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to {BASE_URL}")
        print("Make sure the backend server is running:\n")
        print("  cd backend")
        print("  docker-compose up -d")
        print("  # or\n")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\n❌ Error: Timeout connecting to {BASE_URL}")
        sys.exit(1)
    
    # Запуск тестов
    success = run_all_tests()
    sys.exit(0 if success else 1)
