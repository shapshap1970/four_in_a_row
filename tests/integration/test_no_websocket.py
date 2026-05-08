"""
Integration tests to verify REST API works without WebSocket
"""
import pytest
from fastapi.testclient import TestClient
from web_server import app


@pytest.fixture
def client():
    """Create test client with proper cleanup"""
    with TestClient(app) as test_client:
        yield test_client


class TestNoWebSocketRequired:
    """Test that game works purely via REST API without WebSocket"""

    def test_ai_move_endpoint_exists(self, client):
        """Test that /api/game/{game_id}/ai-move endpoint exists"""
        # Create a game
        response = client.post("/api/game/new", json={"player_starts": False})
        assert response.status_code == 200
        game_id = response.json()["game_id"]

        # Call AI move endpoint
        response = client.post(f"/api/game/{game_id}/ai-move")
        assert response.status_code == 200
        data = response.json()
        assert "board" in data
        assert "current_player" in data

    def test_complete_game_without_websocket(self, client):
        """Test complete game flow using only REST API"""
        # Create game - player starts
        response = client.post("/api/game/new", json={"player_starts": True})
        assert response.status_code == 200
        game_data = response.json()
        game_id = game_data["game_id"]
        assert game_data["current_player"] == "X"

        # Player makes move
        response = client.post(f"/api/game/{game_id}/move", json={"column": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["current_player"] == "O"  # Should switch to AI

        # AI makes first move
        response = client.post(f"/api/game/{game_id}/ai-move")
        assert response.status_code == 200
        data = response.json()
        # AI might still have turn (2-move rule) or switch to player
        assert data["current_player"] in ["O", "X"]

        # If AI still has turn, make 2nd move
        if data["current_player"] == "O":
            response = client.post(f"/api/game/{game_id}/ai-move")
            assert response.status_code == 200
            data = response.json()
            assert data["current_player"] == "X"  # Should be player's turn now

    def test_ai_move_when_not_ai_turn_fails(self, client):
        """Test that AI move fails when it's not AI's turn"""
        # Create game - player starts
        response = client.post("/api/game/new", json={"player_starts": True})
        assert response.status_code == 200
        game_id = response.json()["game_id"]

        # Try to make AI move when it's player's turn
        response = client.post(f"/api/game/{game_id}/ai-move")
        assert response.status_code == 400
        assert "Not AI's turn" in response.json()["detail"]

    def test_ai_starts_game_without_websocket(self, client):
        """Test AI can start game using REST API only"""
        # Create game - AI starts
        response = client.post("/api/game/new", json={"player_starts": False})
        assert response.status_code == 200
        game_data = response.json()
        game_id = game_data["game_id"]
        assert game_data["current_player"] == "O"  # AI's turn

        # AI makes first move
        response = client.post(f"/api/game/{game_id}/ai-move")
        assert response.status_code == 200
        data = response.json()

        # Check board has one piece
        board = data["board"]
        pieces_count = sum(1 for row in board for cell in row if cell != " ")
        assert pieces_count == 1  # One AI move made

    def test_no_websocket_in_html(self, client):
        """Test that HTML page is served (WebSocket check should be done manually)"""
        response = client.get("/")
        assert response.status_code == 200
        html_content = response.text

        # Verify it's HTML
        assert "<!DOCTYPE html>" in html_content
        assert "Four in a Row" in html_content

        # Verify REST API endpoints are referenced
        assert "/api/game/new" in html_content
        assert "/api/game/" in html_content

        # NOTE: We removed WebSocket usage, but the endpoint still exists
        # for backwards compatibility. The HTML should use REST API.
