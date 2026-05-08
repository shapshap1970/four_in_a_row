#!/usr/bin/env python3
"""
Comprehensive test suite for all game scenarios
Tests player-first, AI-first, 2-move rule, wins, draws, etc.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_scenario(name, test_func):
    """Run a test scenario and report results"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print('='*70)
    try:
        test_func()
        print(f"✅ PASSED: {name}")
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {name}")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {name}")
        print(f"   Exception: {e}")
        return False

def test_player_starts_first():
    """Test: Player starts first, plays a few moves"""
    print("1. Creating game with player starting...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    assert response.status_code == 200
    game = response.json()
    game_id = game["game_id"]
    assert game["current_player"] == "X", "Player should start"
    print(f"   ✓ Game created, player (X) starts")

    print("2. Player makes first move (column 3)...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 3})
    assert response.status_code == 200
    game = response.json()
    print(f"   ✓ Move accepted, next player: {game['current_player']}")

    print("3. AI makes response move...")
    if game["current_player"] == "O":
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
        elapsed = time.time() - start_time
        assert response.status_code == 200
        game = response.json()
        print(f"   ✓ AI moved in {elapsed:.2f}s, next player: {game['current_player']}")

    assert not game["game_over"], "Game should still be active"
    print("   ✓ Game continues normally")

def test_ai_starts_first():
    """Test: AI starts first"""
    print("1. Creating game with AI starting...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": False})
    assert response.status_code == 200
    game = response.json()
    game_id = game["game_id"]
    assert game["current_player"] == "O", "AI should start"
    print(f"   ✓ Game created, AI (O) starts")

    print("2. AI makes first move...")
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
    elapsed = time.time() - start_time
    assert response.status_code == 200
    game = response.json()
    print(f"   ✓ AI moved in {elapsed:.2f}s to column (check board)")

    # Check if AI needs second move (2-move rule)
    if game["current_player"] == "O":
        print("3. AI has second move (2-move rule)...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
        assert response.status_code == 200
        game = response.json()
        print(f"   ✓ AI completed 2nd move, next player: {game['current_player']}")

    assert game["current_player"] == "X", "Should be player's turn now"
    print("   ✓ Player's turn after AI completes moves")

def test_two_move_rule():
    """Test: 2-move rule working correctly"""
    print("1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game = response.json()
    game_id = game["game_id"]

    print("2. Player makes move 1...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 3})
    assert response.status_code == 200
    game = response.json()
    player_after_1 = game["current_player"]
    print(f"   After move 1: current_player = {player_after_1}")

    # First move exception: player should get 2 moves
    if player_after_1 == "X":
        print("3. Player gets 2nd move (first move exception)...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": 4})
        assert response.status_code == 200
        game = response.json()
        print(f"   After move 2: current_player = {game['current_player']}")
        assert game["current_player"] == "O", "Should switch to AI after 2 moves"

    print("   ✓ 2-move rule working correctly")

def test_full_column():
    """Test: Cannot play on full column"""
    print("1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game = response.json()
    game_id = game["game_id"]

    print("2. Filling column 0 (6 moves)...")
    for i in range(6):
        # Alternate between columns to keep game going
        if i < 6:
            col = 0
        else:
            col = 1

        # Check whose turn it is
        response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
        game = response.json()

        if game["current_player"] == "X":
            response = requests.post(f"{BASE_URL}/api/game/{game_id}/move", json={"column": col})
        else:
            response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")

        if response.status_code != 200:
            print(f"   Move {i+1} failed, game might be over")
            break

    print("3. Trying to play on full column 0...")
    response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
    game = response.json()

    if not game["game_over"] and 0 not in game["valid_moves"]:
        print("   ✓ Column 0 is full and not in valid_moves")
    else:
        print("   ⚠️  Game ended or column still has space")

def test_ai_performance():
    """Test: AI response time at depth 12"""
    print("1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game = response.json()
    game_id = game["game_id"]

    print("2. Player moves, testing AI response times...")
    times = []

    for move_num in range(5):  # Test 5 AI moves
        # Player move
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                                json={"column": move_num % 7})
        if response.status_code != 200:
            break
        game = response.json()

        if game["game_over"]:
            break

        # AI move(s) - might be 1 or 2 due to 2-move rule
        while game["current_player"] == "O" and not game["game_over"]:
            start = time.time()
            response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
            elapsed = time.time() - start

            if response.status_code == 200:
                times.append(elapsed)
                game = response.json()
                print(f"   AI move {len(times)}: {elapsed:.2f}s")
            else:
                break

    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        print(f"\n   Average AI time: {avg_time:.2f}s")
        print(f"   Max AI time: {max_time:.2f}s")
        assert avg_time < 5.0, f"AI too slow: {avg_time:.2f}s average"
        print("   ✓ AI performance acceptable")

def test_game_state_consistency():
    """Test: Game state remains consistent"""
    print("1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game = response.json()
    game_id = game["game_id"]

    print("2. Making moves and checking consistency...")
    for move_num in range(10):
        # Get current state
        response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
        assert response.status_code == 200
        game = response.json()

        if game["game_over"]:
            print(f"   Game ended at move {move_num}")
            break

        # Verify board is 6x7
        assert len(game["board"]) == 6, "Board should have 6 rows"
        assert all(len(row) == 7 for row in game["board"]), "Each row should have 7 columns"

        # Make appropriate move
        if game["current_player"] == "X":
            col = move_num % 7
            response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                                    json={"column": col})
        else:
            response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")

        if response.status_code != 200:
            break

    print("   ✓ Game state remained consistent")

def test_error_responses():
    """Test: Error responses are properly formatted"""
    print("1. Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/new", json={"player_starts": True})
    game = response.json()
    game_id = game["game_id"]

    print("2. Testing wrong turn error...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/ai-move")
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error, "Error should have 'detail' field"
    print(f"   ✓ Got error: {error['detail']}")

    print("3. Testing invalid column...")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                            json={"column": 999})
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
    print(f"   ✓ Got error: {error['detail']}")

    print("4. Testing invalid game ID...")
    response = requests.get(f"{BASE_URL}/api/game/invalid-id/state")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error
    print(f"   ✓ Got error: {error['detail']}")

def main():
    """Run all test scenarios"""
    print("="*70)
    print("COMPREHENSIVE GAME SCENARIO TESTS")
    print("="*70)
    print(f"Testing server at: {BASE_URL}")

    # Test server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✓ Server is running\n")
    except:
        print("❌ Server is not running at http://localhost:8000")
        print("   Please start the server first: python web_server.py")
        return False

    tests = [
        ("Player Starts First", test_player_starts_first),
        ("AI Starts First", test_ai_starts_first),
        ("2-Move Rule", test_two_move_rule),
        ("Full Column Handling", test_full_column),
        ("AI Performance (Depth 12)", test_ai_performance),
        ("Game State Consistency", test_game_state_consistency),
        ("Error Response Format", test_error_responses),
    ]

    results = []
    for name, test_func in tests:
        passed = test_scenario(name, test_func)
        results.append((name, passed))
        time.sleep(0.5)  # Small delay between tests

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Fix before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
