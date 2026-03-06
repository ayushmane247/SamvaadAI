import time
import uuid
from typing import Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError

from core.config import config


# ==============================
# Module-level Initialization
# ==============================

_dynamodb_resource = boto3.resource(
    "dynamodb",
    region_name=config.AWS_REGION,
)

_table = _dynamodb_resource.Table(config.DYNAMODB_TABLE_NAME)


# ==============================
# Internal Helpers
# ==============================

def _epoch_now() -> int:
    return int(time.time())


def _new_ttl() -> int:
    return _epoch_now() + config.SESSION_TTL_SECONDS


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ==============================
# Session Service
# ==============================

class SessionService:
    """
    Persistence layer only.
    No business logic.
    No LLM logic.
    No rule engine calls.
    """

    def __init__(self, table=None):
        # Dependency injection support for tests
        self._table = table or _table

    # --------------------------
    # CREATE
    # --------------------------
    def create_session(self) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        now_iso = _utc_iso()

        item = {
            "session_id": session_id,
            "structured_profile": {},
            "conversation_state": {},
            "evaluation_result": None,
            "ttl": _new_ttl(),
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        self._table.put_item(Item=item)

        return item

    # --------------------------
    # READ
    # --------------------------
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self._table.get_item(
                Key={"session_id": session_id}
            )
        except ClientError:
            raise

        return response.get("Item")

    # --------------------------
    # UPDATE
    # --------------------------
    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Allowed update keys:
            structured_profile
            conversation_state
            evaluation_result
        """

        allowed = {
            "structured_profile",
            "conversation_state",
            "evaluation_result",
        }

        invalid = set(updates.keys()) - allowed
        if invalid:
            raise ValueError(f"Invalid update fields: {invalid}")

        updates = updates.copy()
        updates["ttl"] = _new_ttl()
        updates["updated_at"] = _utc_iso()

        expression_parts = []
        attr_values = {}
        attr_names = {}

        for key, value in updates.items():
            name_placeholder = f"#{key}"
            value_placeholder = f":{key}"

            expression_parts.append(f"{name_placeholder} = {value_placeholder}")
            attr_names[name_placeholder] = key
            attr_values[value_placeholder] = value

        update_expression = "SET " + ", ".join(expression_parts)

        response = self._table.update_item(
            Key={"session_id": session_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
            ReturnValues="ALL_NEW",
        )

        return response["Attributes"]

    # --------------------------
    # DELETE
    # --------------------------
    def delete_session(self, session_id: str) -> None:
        self._table.delete_item(
            Key={"session_id": session_id}
        )