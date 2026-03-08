from llm_service.bedrock_client import get_client

def main():
    client = get_client()

    prompt = "Explain what AWS Bedrock is in 2 sentences."

    response = client.invoke_model_with_response_stream(prompt)

    print("\n=== MODEL RESPONSE ===\n")
    print(response)

if __name__ == "__main__":
    main()