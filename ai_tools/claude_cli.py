# ai_tools\claude_cli.py

import boto3
import json
import argparse
from config import AWS_REGION, MODEL_ID, MAX_TOKENS, TEMPERATURE, SYSTEM_PROMPT


def call_claude(user_prompt: str):
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }

    response = client.invoke_model(
    modelId=MODEL_ID,
    body=json.dumps(body),
    contentType="application/json",
    accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to prompt file")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        prompt = f.read()

    print("\n--- Claude Response ---\n")
    print(call_claude(prompt))


if __name__ == "__main__":
    main()