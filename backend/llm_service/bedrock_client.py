"""
Amazon Bedrock Client Wrapper.

Singleton client for Anthropic Claude models via AWS Bedrock.
Initialized once at module level, reused across all requests.

Architectural guarantees:
- Single boto3 client per process (Lambda container reuse)
- Retry with exponential backoff (2 attempts)
- Timeout protection (configurable)
- Structured error handling
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
            ClientError: If the Bedrock API call fails.
            TimeoutError: If the request exceeds the configured timeout.
            ValueError: If the response cannot be parsed.
        """
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
            text = result.get("content", [{}])[0].get("text", "")

            if not text:
                logger.warning("Bedrock returned empty response")
                raise ValueError("Empty response from Bedrock")

            return text

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ThrottlingException":
                logger.warning("Bedrock rate limited, retrying may help")
            logger.error(f"Bedrock API error: {error_code}")
            raise

        except BotoCoreError as e:
            logger.error(f"Bedrock connection error: {e}")
            raise

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