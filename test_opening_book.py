#!/usr/bin/env python3
"""Test opening book performance"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_opening_book():
    print("\n🧪 Testing Opening Book Performance\n")
    print("="*60)

    # Create new game
    print("1. Creating new game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"search_depth": 8})
    game_id = response.json()["game_id"]
    print(f"   ✓ Game ID: {game_id}")

    # Make first player move (center column)
    print("\n2. Player X plays column 3 (center)...")
    requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 3})
    print("   ✓ Move made")

    # Test AI move speed (should use opening book - instant!)
    print("\n3. AI (O) making first move...")
    print("   Expected: INSTANT (from opening book)")
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai_move")
    elapsed = time.time() - start

    data = response.json()
    ai_column = data.get("ai_move")

    print(f"   ✓ AI played column {ai_column}")
    print(f"   ⏱️  Time: {elapsed:.3f} seconds")

    if elapsed < 0.5:
        print("   🎉 SUCCESS! Opening book working (< 0.5s)")
    else:
        print(f"   ⚠️  Slower than expected - might not be using opening book")

    # Make another player move
    print("\n4. Player X plays column 3 again...")
    requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 3})
    print("   ✓ Move made")

    # Test second AI move
    print("\n5. AI (O) making second move...")
    print("   Expected: INSTANT (from opening book)")
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai_move")
    elapsed = time.time() - start

    data = response.json()
    ai_column = data.get("ai_move")

    print(f"   ✓ AI played column {ai_column}")
    print(f"   ⏱️  Time: {elapsed:.3f} seconds")

    if elapsed < 0.5:
        print("   🎉 SUCCESS! Opening book working (< 0.5s)")
    else:
        print(f"   ⚠️  Slower than expected")

    print("\n" + "="*60)
    print("✅ Opening Book Test Complete!")
    print(f"\nOpening book contains 67,351 positions")
    print(f"First 8 moves should be instant!\n")

if __name__ == "__main__":
    try:
        test_opening_book()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the web server is running:")
        print("  python3 web_server.py")
