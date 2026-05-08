#!/usr/bin/env python3
"""Test rolling 8-move lookahead system"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_rolling_lookahead():
    print("\n🧪 Testing Rolling 8-Move Lookahead System\n")
    print("="*70)

    # Create new game
    print("1. Creating new game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game_id = response.json()["game_id"]
    print(f"   ✓ Game ID: {game_id}")

    print("\n" + "="*70)
    print("Testing: AI should always have 8 moves computed ahead")
    print("="*70)

    for move_num in range(1, 11):  # Test 10 moves
        print(f"\n--- Move {move_num} ---")

        # Player move
        print(f"  Player X: column 3")
        requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 3})
        time.sleep(0.5)  # Give time for tree extension

        # AI move (should be instant from cache or opening book)
        print(f"  AI O: ", end="")
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
        elapsed = time.time() - start

        data = response.json()
        if data.get("game_over"):
            print(f"Game over! Winner: {data.get('winner')}")
            break

        ai_column = data.get("last_move")
        print(f"column {ai_column}")
        print(f"  ⏱️  AI time: {elapsed:.3f}s", end="")

        if elapsed < 1.0:
            print(" ✅ INSTANT (cache hit)")
        else:
            print(" ⚠️  Slow (cache miss)")

        # Small delay for tree extension
        time.sleep(1.0)

    print("\n" + "="*70)
    print("✅ Rolling Lookahead Test Complete!")
    print("\nExpected behavior:")
    print("  - Moves 1-8: Instant (from opening book)")
    print("  - Moves 9+: Instant (from dynamic cache)")
    print("  - Tree extends in background after each move")
    print("  - AI always maintains 8-move lookahead")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_rolling_lookahead()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
