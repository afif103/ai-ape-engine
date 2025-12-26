"""Tests for chat endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestChat:
    """Test chat functionality."""

    def test_create_conversation(self, client: TestClient, auth_headers: dict):
        """Test creating a new conversation."""
        conversation_data = {"title": "Test Conversation"}

        response = client.post(
            "/api/v1/chat/conversations", json=conversation_data, headers=auth_headers
        )

        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Conversation"
        assert "created_at" in data
        assert "updated_at" in data

        # Store conversation ID for other tests
        self.conversation_id = data["id"]

    def test_list_conversations(self, client: TestClient, auth_headers: dict):
        """Test listing user conversations."""
        # First create a conversation
        conversation_data = {"title": "List Test"}
        response = client.post(
            "/api/v1/chat/conversations", json=conversation_data, headers=auth_headers
        )
        assert response.status_code == 201

        # Now list conversations
        response = client.get("/api/v1/chat/conversations", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check structure of first conversation
        conv = data[0]
        assert "id" in conv
        assert "title" in conv
        assert "created_at" in conv

    def test_send_message(self, client: TestClient, auth_headers: dict):
        """Test sending a message and getting AI response."""
        # Create conversation first
        conversation_data = {"title": "Message Test"}
        response = client.post(
            "/api/v1/chat/conversations", json=conversation_data, headers=auth_headers
        )
        assert response.status_code == 201
        conversation_id = response.json()["id"]

        # Send message
        message_data = {"content": "Hello, can you help me with a simple Python question?"}

        response = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json=message_data,
            headers=auth_headers,
        )

        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "provider" in data
        assert "model" in data

        # Check message structure
        message = data["message"]
        assert "id" in message
        assert "role" in message
        assert "content" in message
        assert message["role"] == "assistant"
        assert len(message["content"]) > 0

    def test_get_conversation_with_messages(self, client: TestClient, auth_headers: dict):
        """Test getting conversation with messages."""
        # Create conversation and send message
        conversation_data = {"title": "Full Test"}
        response = client.post(
            "/api/v1/chat/conversations", json=conversation_data, headers=auth_headers
        )
        conversation_id = response.json()["id"]

        message_data = {"content": "What is Python?"}
        client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json=message_data,
            headers=auth_headers,
        )

        # Get conversation with messages
        response = client.get(f"/api/v1/chat/conversations/{conversation_id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "messages" in data
        assert "token_stats" in data

        # Should have at least user and assistant messages
        assert len(data["messages"]) >= 2

    def test_unauthorized_access(self, client: TestClient):
        """Test accessing chat endpoints without authentication."""
        response = client.post("/api/v1/chat/conversations", json={"title": "Test"})

        assert response.status_code == 401

    def test_access_other_user_conversation(self, client: TestClient):
        """Test that users can't access other users' conversations."""
        # This would require creating two users and testing cross-access
        # For now, just ensure authentication is required
        response = client.get("/api/v1/chat/conversations/some-uuid")

        assert response.status_code == 401
