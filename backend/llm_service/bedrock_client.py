"""
Amazon Bedrock Client Wrapper.

Singleton client for Anthropic Claude models via AWS Bedrock.
Initialized once at module level, reused across all requests.

Architectural guarantees:
- Single boto3 client per process (Lambda container reuse)
- Retry with exponential backoff (2 attempts)
- Timeout protection (configurable)
- Structured error handling
- Graceful fallback on AccessDeniedException / INVALID_PAYMENT_INSTRUMENT
"""

import json
import logging
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config

from llm_service.config import (
    MODEL_ID,
    REGION,
    TEMPERATURE,
    MAX_TOKENS,
    TIMEOUT_SECONDS,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

logger = logging.getLogger(__name__)


# =====================================
# Custom Exception
# =====================================

class BedrockUnavailableError(Exception):
    """
    Raised when Bedrock is unavailable due to billing or access issues.

    Triggers:
    - AccessDeniedException
    - INVALID_PAYMENT_INSTRUMENT
    - UnrecognizedClientException

    When raised, the system should fallback to deterministic processing.
    """

    def __init__(self, error_code: str, message: str = ""):
        self.error_code = error_code
        super().__init__(f"Bedrock unavailable ({error_code}): {message}")


# Error codes that indicate Bedrock is fundamentally unavailable
_UNAVAILABLE_ERROR_CODES = {
    "AccessDeniedException",
    "UnrecognizedClientException",
    "ValidationException",
}

# Error messages that indicate payment issues
_PAYMENT_ERROR_PHRASES = {
    "INVALID_PAYMENT_INSTRUMENT",
    "payment instrument",
    "billing",
    "subscription",
}

# Module-level availability flag
_bedrock_available: bool = True


def is_available() -> bool:
    """Check if Bedrock is currently available."""
    return _bedrock_available


def _mark_unavailable(error_code: str):
    """Mark Bedrock as unavailable after a fatal error."""
    global _bedrock_available
    _bedrock_available = False
    logger.warning(
        f"Bedrock marked UNAVAILABLE due to: {error_code}. "
        "System will use deterministic fallback."
    )


class BedrockClient:
    """
    Reusable client for Amazon Bedrock Anthropic Claude models.

    Use get_client() to obtain the module-level singleton instance
    instead of constructing directly.
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self.model_id = model_id or MODEL_ID
        self.region = region or REGION
        self.timeout = timeout or TIMEOUT_SECONDS

        boto_config = Config(
            region_name=self.region,
            retries={"max_attempts": 2, "mode": "standard"},
            connect_timeout=self.timeout,
            read_timeout=self.timeout,
        )

        try:
            kwargs = {
                "service_name": "bedrock-runtime",
                "region_name": self.region,
                "config": boto_config,
            }
            # Use explicit credentials only if provided (prefer IAM roles)
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

            self.client = boto3.client(**kwargs)
            logger.info(f"Bedrock client initialized for model: {self.model_id}")

        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def invoke_model(self, prompt: str) -> str:
        """
        Send a prompt to the Bedrock Claude model and return the text response.

        Uses the Anthropic Messages API format required by Bedrock.

        Args:
            prompt: The user prompt string.

        Returns:
            The model's text response.

        Raises:
            BedrockUnavailableError: If Bedrock is unavailable (billing/access).
            ClientError: If the Bedrock API call fails for other reasons.
            TimeoutError: If the request exceeds the configured timeout.
            ValueError: If the response cannot be parsed.
        """
        # Fast-fail if we already know Bedrock is down
        if not _bedrock_available:
            raise BedrockUnavailableError(
                "CACHED", "Bedrock was previously marked unavailable"
            )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        })

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            result = json.loads(response["body"].read())
            text = "".join(
                block.get("text", "")
                for block in result.get("content", [])
                if block.get("type") == "text"
            )

            if not text:
                logger.warning("Bedrock returned empty response")
                raise ValueError("Empty response from Bedrock")

            return text

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"].get("Message", "")

            # Check for fatal unavailability errors
            if error_code in _UNAVAILABLE_ERROR_CODES:
                _mark_unavailable(error_code)
                raise BedrockUnavailableError(error_code, error_message)

            # Check for payment-related error messages
            for phrase in _PAYMENT_ERROR_PHRASES:
                if phrase.lower() in error_message.lower():
                    _mark_unavailable(f"{error_code}:{phrase}")
                    raise BedrockUnavailableError(error_code, error_message)

            if error_code == "ThrottlingException":
                logger.warning("Bedrock rate limited, retrying may help")

            logger.error(f"Bedrock API error: {error_code}")
            raise

        except BotoCoreError as e:
            logger.error(f"Bedrock connection error: {e}")
            raise

        except BedrockUnavailableError:
            raise  # Re-raise without wrapping

        except Exception as e:
            logger.error(f"Bedrock invoke_model failed: {e}")
            raise


# =====================================
# Module-Level Singleton
# =====================================

_instance: Optional[BedrockClient] = None


def get_client() -> BedrockClient:
    """
    Return the module-level singleton BedrockClient.

    Creates the client on first call, reuses on all subsequent calls.
    Safe for Lambda container reuse.
    """
    global _instance
    if _instance is None:
        _instance = BedrockClient()
    return _instance