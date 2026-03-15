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
import time
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


_UNAVAILABLE_ERROR_CODES = {
    "AccessDeniedException",
    "UnrecognizedClientException",
    "ValidationException",
}

_PAYMENT_ERROR_PHRASES = {
    "INVALID_PAYMENT_INSTRUMENT",
    "payment instrument",
    "billing",
    "subscription",
}

_bedrock_available: bool = True


def is_available() -> bool:
    return _bedrock_available


def _mark_unavailable(error_code: str):
    global _bedrock_available
    _bedrock_available = False
    logger.warning(
        f"Bedrock marked UNAVAILABLE due to: {error_code}. "
        "System will use deterministic fallback."
    )


class BedrockClient:

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

            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

            self.client = boto3.client(**kwargs)

            logger.info(f"Bedrock client initialized for model: {self.model_id}")

        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def invoke_model_with_response_stream(self, prompt: str) -> str:

        if not _bedrock_available:
            raise BedrockUnavailableError(
                "CACHED", "Bedrock was previously marked unavailable"
            )

        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": MAX_TOKENS,
                "temperature": TEMPERATURE
            }
        })

        logger.info(
            "Invoking Bedrock model",
            extra={
                "model_id": self.model_id,
                "region": self.region,
                "prompt_length": len(prompt),
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
            },
        )

        try:
            invoke_start = time.time()

            # FIX 1: Use invoke_model (not streaming)
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            invoke_latency = (time.time() - invoke_start) * 1000

            # FIX 2: Parse response with multi-format support
            result = json.loads(response["body"].read())

            # Handle multiple Bedrock response formats
            text = None
            
            if "output" in result and "message" in result["output"]:
                # Nova format: {"output": {"message": {"content": [{"text": "..."}]}}}
                text = result["output"]["message"]["content"][0]["text"]
            elif "content" in result:
                # Claude format: {"content": [{"text": "..."}]}
                text = result["content"][0]["text"]
            elif "completion" in result:
                # Legacy format: {"completion": "..."}
                text = result["completion"]
            else:
                logger.error(f"Unknown Bedrock response format. Keys: {list(result.keys())}")
                raise ValueError(f"Unexpected Bedrock response structure: {list(result.keys())}")

            if not text:
                logger.warning("Bedrock returned empty response")
                raise ValueError("Empty response from Bedrock")

            logger.info(
                "Bedrock invocation successful",
                extra={
                    "model_id": self.model_id,
                    "latency_ms": round(invoke_latency, 2),
                    "response_length": len(text),
                    "response_format": "nova" if "output" in result else "claude" if "content" in result else "legacy",
                },
            )

            return text

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"].get("Message", "")

            logger.error(
                "Bedrock ClientError",
                extra={
                    "error_code": error_code,
                    "error_message": error_message,
                    "model_id": self.model_id,
                },
            )

            if error_code in _UNAVAILABLE_ERROR_CODES:
                _mark_unavailable(error_code)
                raise BedrockUnavailableError(error_code, error_message)

            for phrase in _PAYMENT_ERROR_PHRASES:
                if phrase.lower() in error_message.lower():
                    _mark_unavailable(f"{error_code}:{phrase}")
                    raise BedrockUnavailableError(error_code, error_message)

            if error_code == "ThrottlingException":
                logger.warning("Bedrock rate limited, retrying once after backoff")
                time.sleep(2)
                return self.invoke_model_with_response_stream(prompt)

            logger.error(f"Bedrock API error: {error_code}")
            raise

        except BotoCoreError as e:
            logger.error(f"Bedrock connection error: {e}")
            raise

        except BedrockUnavailableError:
            raise

        except Exception as e:
            logger.error(f"Bedrock invoke_model failed: {e}")
            raise


_instance: Optional[BedrockClient] = None


def get_client() -> BedrockClient:

    global _instance

    if _instance is None:
        _instance = BedrockClient()

    return _instance