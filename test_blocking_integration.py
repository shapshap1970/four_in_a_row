#!/usr/bin/env python3
"""Integration test - verify AI blocks immediate threats"""

import sys
import asyncio
from fastapi.testclient import TestClient

# Import after path setup
sys.path.insert(0, '.')
from web_server import app

client = TestClient(app)

def test_ai_blocks_threat():
    """Test that AI blocks when human has 3 in a row"""

    # Create game
    response = client.post("/api/game/new", json={"player_starts": True})
    assert response.status_code == 200
    game_id = response.json()["game_id"]
    print(f"Game created: {game_id}")

    # Human plays: 3, 3 (build in center)
    client.post(f"/api/game/{game_id}/move", json={"column": 3})
    client.post(f"/api/game/{game_id}/move", json={"column": 3})

    # AI plays 2 moves
    client.post(f"/api/game/{game_id}/ai-move")

    # Human plays: 2, 4 (now has pieces at 2, 3, 4 in row 5 - needs to complete!)
    client.post(f"/api/game/{game_id}/move", json={"column": 2})
    client.post(f"/api/game/{game_id}/move", json={"column": 4})

    # AI's turn - should block column 1 or 5 to prevent horizontal win!
    response = client.post(f"/api/game/{game_id}/ai-move")
    state = response.json()

    # Check AI's last move
    board = state["board"]
    print("\nBoard after AI blocks:")
    for row in board:
        print("  " + " ".join(row))

    # AI should have blocked in row with human's 3-piece threat
    # If AI didn't block, human can win next turn
    response = client.post(f"/api/game/{game_id}/move", json={"column": 1})
    state = response.json()

    if state["game_over"] and state["winner"] == "X":
        print("\n❌ FAILED: AI didn't block, human won!")
        return False
    else:
        print("\n✓ PASSED: AI blocked the threat or game continues")
        return True

if __name__ == "__main__":
    result = test_ai_blocks_threat()
    sys.exit(0 if result else 1)
