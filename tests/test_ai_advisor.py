import json
from unittest.mock import MagicMock, patch

from ai_advisor import suggest_tasks


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_suggest_tasks_returns_valid_tasks():
    payload = json.dumps({
        "tasks": [
            {"name": "Morning Walk", "duration": 30, "priority": "high", "category": "walk"},
            {"name": "Feeding", "duration": 10, "priority": "high", "category": "feed"},
            {"name": "Playtime", "duration": 15, "priority": "medium", "category": "play"},
        ]
    })
    with patch("ai_advisor.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _mock_response(payload)
        result = suggest_tasks("Luna", "dog", 4)

    assert result["success"] is True
    assert len(result["tasks"]) == 3
    assert result["confidence"] == 1.0
    assert result["error"] is None


def test_suggest_tasks_invalid_json_returns_failure():
    with patch("ai_advisor.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _mock_response("not valid json at all")
        result = suggest_tasks("Mochi", "cat", 3)

    assert result["success"] is False
    assert result["confidence"] == 0.0
    assert result["tasks"] == []
    assert "invalid JSON" in result["error"]


def test_suggest_tasks_malformed_tasks_lower_confidence():
    payload = json.dumps({
        "tasks": [
            {"name": "Walk", "duration": 30, "priority": "high", "category": "walk"},
            {"name": "Bad task", "duration": "oops", "priority": "medium", "category": "play"},
        ]
    })
    with patch("ai_advisor.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _mock_response(payload)
        result = suggest_tasks("Buddy", "dog", 2)

    assert result["success"] is True
    assert len(result["tasks"]) == 1
    assert result["confidence"] == 0.5


def test_suggest_tasks_api_error_returns_failure():
    with patch("ai_advisor.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.side_effect = Exception("network timeout")
        result = suggest_tasks("Mochi", "cat", 3)

    assert result["success"] is False
    assert "network timeout" in result["error"]
    assert result["confidence"] == 0.0


def test_suggest_tasks_unknown_category_dropped():
    payload = json.dumps({
        "tasks": [
            {"name": "Walk", "duration": 30, "priority": "high", "category": "walk"},
            {"name": "Spa Day", "duration": 60, "priority": "low", "category": "spa"},  # invalid category
        ]
    })
    with patch("ai_advisor.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _mock_response(payload)
        result = suggest_tasks("Mochi", "cat", 5)

    assert result["success"] is True
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["name"] == "Walk"
