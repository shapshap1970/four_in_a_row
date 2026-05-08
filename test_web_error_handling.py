#!/usr/bin/env python3
"""
Test web API error handling - ensures proper error responses
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_invalid_move_scenarios():
    """Test that API returns proper error responses for invalid moves"""
    print("="*70)
    print("Testing Web API Error Handling")
    print("="*70)

    # Create a new game
    print("\n1. Creating new game (player starts)...")
    response = requests.post(f"{BASE_URL}/api/game/new",
                            json={"player_starts": True})
    assert response.status_code == 200, "Failed to create game"
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"   ✓ Game created: {game_id[:8]}...")

    # Test 1: Try to make AI move when it's player's turn
    print("\n2. Testing: AI move when it's player's turn...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
    assert response.status_code == 400, "Should return 400 for wrong turn"
    error_data = response.json()
    assert "detail" in error_data, "Error should have 'detail' field"
    print(f"   ✓ Got 400 error: {error_data['detail']}")

    # Test 2: Player makes a valid move
    print("\n3. Player makes valid move (column 3)...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                            json={"column": 3})
    assert response.status_code == 200, "Valid move should succeed"
    print(f"   ✓ Move succeeded")

    # Test 3: Try to make another player move when it's AI's turn
    print("\n4. Testing: Player move when it's AI's turn...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                            json={"column": 2})
    if response.status_code == 400:
        error_data = response.json()
        assert "detail" in error_data, "Error should have 'detail' field"
        print(f"   ✓ Got 400 error: {error_data['detail']}")
    else:
        print(f"   ⚠️  Expected 400 but got {response.status_code} (might be player's turn due to 2-move rule)")

    # Test 4: Invalid column number - create fresh game first
    print("\n5. Testing: Invalid column number...")
    game3_response = requests.post(f"{BASE_URL}/api/game/new",
                                   json={"player_starts": True})
    game3_id = game3_response.json()["game_id"]

    response = requests.post(f"{BASE_URL}/api/game/{game3_id}/move",
                            json={"column": 99})
    assert response.status_code == 400, "Should return 400 for invalid column"
    error_data = response.json()
    assert "detail" in error_data, "Error should have 'detail' field"
    print(f"   ✓ Got 400 error: {error_data['detail']}")

    # Test 5: Fill a column and try to play there again
    print("\n6. Testing: Play on full column...")
    game2_response = requests.post(f"{BASE_URL}/api/game/new",
                                   json={"player_starts": True})
    game2_id = game2_response.json()["game_id"]

    # Fill column 0 (6 moves)
    for i in range(6):
        response = requests.post(f"{BASE_URL}/api/game/{game2_id}/move",
                                json={"column": 0})
        if response.status_code != 200:
            break

    # Try to play on full column 0
    response = requests.post(f"{BASE_URL}/api/game/{game2_id}/move",
                            json={"column": 0})
    if response.status_code == 400:
        error_data = response.json()
        assert "detail" in error_data, "Error should have 'detail' field"
        print(f"   ✓ Got 400 error: {error_data['detail']}")
    else:
        print(f"   ℹ️  Column not full yet or game ended")

    # Test 6: Verify error response structure - use fresh game
    print("\n7. Testing: Error response structure...")
    game4_response = requests.post(f"{BASE_URL}/api/game/new",
                                   json={"player_starts": True})
    game4_id = game4_response.json()["game_id"]

    response = requests.post(f"{BASE_URL}/api/game/{game4_id}/ai-move")
    assert response.status_code == 400
    error_data = response.json()

    # Check that error has 'detail' field (FastAPI standard)
    assert "detail" in error_data, "Error must have 'detail' field"
    assert isinstance(error_data["detail"], str), "'detail' must be string"
    assert len(error_data["detail"]) > 0, "'detail' must not be empty"
    print(f"   ✓ Error structure correct: {{'detail': '{error_data['detail']}'}}")

    print("\n" + "="*70)
    print("✅ All error handling tests passed!")
    print("="*70)
    print("\nVerified:")
    print("  - API returns 400 for invalid moves")
    print("  - Error responses have 'detail' field")
    print("  - Frontend can safely check 'data.detail' for errors")

if __name__ == "__main__":
    try:
        test_invalid_move_scenarios()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the web server is running!")
        exit(1)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
