# backend\tests\test_session_service.py

import time
import uuid
import pytest

from session_store.session_service import SessionService


# =====================================================
# In-Memory Fake DynamoDB Table (Dependency Injection)
# =====================================================

class FakeDynamoTable:
    def __init__(self):
        self.store = {}

    def put_item(self, Item):
        self.store[Item["session_id"]] = Item

    def get_item(self, Key):
        session_id = Key["session_id"]
        if session_id in self.store:
            return {"Item": self.store[session_id]}
        return {}

    def update_item(
        self,
        Key,
        UpdateExpression,
        ExpressionAttributeNames,
        ExpressionAttributeValues,
        ReturnValues,
    ):
        session_id = Key["session_id"]
        if session_id not in self.store:
            raise Exception("Session not found")

        item = self.store[session_id]

        # Simulate DynamoDB SET update behavior
        for name_placeholder, actual_name in ExpressionAttributeNames.items():
            value_placeholder = f":{actual_name}"
            if value_placeholder in ExpressionAttributeValues:
                item[actual_name] = ExpressionAttributeValues[value_placeholder]

        self.store[session_id] = item

        return {"Attributes": item}

    def delete_item(self, Key):
        session_id = Key["session_id"]
        self.store.pop(session_id, None)


# =====================================================
# Tests
# =====================================================

@pytest.fixture
def service():
    fake_table = FakeDynamoTable()
    return SessionService(table=fake_table)


# ------------------------------
# 1️⃣ Create Session
# ------------------------------
def test_create_session(service):
    now = int(time.time())

    session = service.create_session()

    # session_id exists and valid UUID
    assert "session_id" in session
    uuid.UUID(session["session_id"])

    assert session["structured_profile"] == {}
    assert session["evaluation_result"] is None

    assert session["ttl"] > now
    assert isinstance(session["ttl"], int)

    assert session["created_at"] == session["updated_at"]


# ------------------------------
# 2️⃣ Get Session
# ------------------------------
def test_get_session_returns_none_for_missing(service):
    result = service.get_session("non-existent")
    assert result is None


def test_get_session_returns_item(service):
    session = service.create_session()
    session_id = session["session_id"]

    result = service.get_session(session_id)

    assert result is not None
    assert result["session_id"] == session_id


# ------------------------------
# 3️⃣ Update Session
# ------------------------------
def test_update_session_updates_profile_and_refreshes_ttl(service):
    session = service.create_session()
    session_id = session["session_id"]

    old_ttl = session["ttl"]
    old_updated_at = session["updated_at"]

    time.sleep(1)

    updated = service.update_session(
        session_id,
        {"structured_profile": {"age": 60}}
    )

    assert updated["structured_profile"] == {"age": 60}
    assert updated["updated_at"] != old_updated_at
    assert updated["ttl"] > old_ttl


def test_update_session_invalid_key_raises(service):
    session = service.create_session()
    session_id = session["session_id"]

    with pytest.raises(ValueError):
        service.update_session(
            session_id,
            {"invalid_field": "not_allowed"}
        )


# ------------------------------
# 4️⃣ Delete Session
# ------------------------------
def test_delete_session_removes_item(service):
    session = service.create_session()
    session_id = session["session_id"]

    service.delete_session(session_id)

    result = service.get_session(session_id)
    assert result is None