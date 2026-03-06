# SamvaadAI LLM Module

A production-ready Python module for integrating Amazon Bedrock (Anthropic Claude) to perform intent extraction and explanation generation for government scheme eligibility systems.

## 🎯 Architecture Principles

**CRITICAL RULES (NON-NEGOTIABLE):**

1. **LLM is ONLY for understanding and explanation** - Never for eligibility decisions
2. **Eligibility decisions are deterministic** - Handled by separate rule engine module
3. **Completely stateless** - No database, no permanent storage
4. **Structured output** - Always predictable JSON format
5. **Fallback system** - Templates used when LLM fails
6. **Safety guardrails** - Prevents LLM from making eligibility decisions

## 📁 Project Structure

```
samvaadai-llm/
│
├── llm_service.py          # Main LLM service
├── bedrock_client.py       # Bedrock client wrapper
├── mock_rule_engine.py     # Mock rule engine (simulates Pranit's module)
├── schema_adapter.py       # Normalizes backend/rule outputs
├── prompts/
│   ├── intent_prompt.txt
│   └── explanation_prompt.txt
├── fallback_templates.py   # Fallback templates (en/hi/mr)
├── config.py               # Configuration
├── integration_test.py     # Full pipeline simulation
├── guardrail_tests.py      # Guardrail validation
├── demo_run.py             # Demo mode runner
├── test_llm.py             # Unit tests
├── env.example             # Environment template
├── requirements.txt
├── README.md
└── FINAL_CHECKLIST.md      # Hackathon completion checklist
```

## 🏛️ Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ User Input  │────▶│ extract_profile  │────▶│ Rule Engine     │────▶│ generate_explanation│
│ (en/hi/mr)  │     │ (LLM - optional) │     │ (deterministic) │     │ (LLM or fallback) │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────────────────┘
```

**Why the rule engine is separate from the LLM:**
- **Determinism:** Eligibility must be auditable and reproducible.
- **Safety:** LLMs can hallucinate; rules cannot.
- **Compliance:** Government schemes require clear, traceable logic.
- **Fallback:** System works even when Bedrock is down (templates).

---

## 🚀 Setup

### Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access (optional for demo; fallbacks work without it)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd samvaadai-llm
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials (optional for demo):**
   - Copy `env.example` to `.env` and add keys when ready. No code changes needed.
   - Demo and integration tests run without credentials (use fallbacks).

   Option A: Environment variables (create `.env` from `env.example`):
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=ap-south-1
   ```

   Option B: AWS credentials file (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```

   Option C: IAM role (if running on EC2/Lambda)

5. **Enable Bedrock model access:**
   - Go to AWS Bedrock console
   - Request access to Anthropic Claude models
   - Wait for approval (usually instant for Claude)

## 📖 Usage

### Basic Usage

```python
from llm_service import extract_user_profile, generate_explanation

# Extract user profile from natural language
user_text = "I am 35 years old, work as a farmer in Maharashtra"
profile = extract_user_profile(user_text, language="en")
print(profile)
# Output: {"age": 35, "occupation": "farmer", "income_band": null, "location": {"state": "Maharashtra"}}

# Generate explanation from rule engine output
rule_output = {
    "scheme": "PM-KISAN",
    "status": "eligible",
    "reason": "occupation=farmer AND income<3L"
}
explanation = generate_explanation(rule_output, language="en")
print(explanation)
# Output: "You are eligible for PM-KISAN because you are a farmer..."
```

### Advanced Usage

```python
from llm_service import LLMService

# Create service instance (reuses Bedrock client)
service = LLMService()

# Extract profile
profile = service.extract_user_profile(
    "मैं ४० साल का हूं, किसान हूं",
    language="hi"
)

# Generate explanation
explanation = service.generate_explanation(
    {
        "scheme": "PM-KISAN",
        "status": "not_eligible",
        "reason": "occupation!=farmer"
    },
    language="hi"
)
```

## 🧪 Testing & Demo

### Run Demo (recommended for judges)
```bash
python demo_run.py
```
Shows full pipeline: user input → profile → scheme decision → explanation. Works without AWS.

### Integration simulation
```bash
python integration_test.py
```
Runs 3 demo flows (English, Hindi, Marathi) with simulated profiles.

### Guardrail validation
```bash
python guardrail_tests.py
```
Verifies LLM never outputs eligibility decisions directly.

### Unit tests
```bash
python test_llm.py
```
Intent extraction, explanation generation, fallback behavior. Works without AWS (fallbacks activate).

## 🌐 Supported Languages

- **English** (`en`)
- **Hindi** (`hi`)
- **Marathi** (`mr`)

## 📋 API Reference

### `extract_user_profile(user_text: str, language: str = "en") -> dict`

Extracts structured user profile from natural language text.

**Parameters:**
- `user_text`: User input text (any language)
- `language`: Language code (`en`, `hi`, `mr`) - used for fallback messages

**Returns:**
```python
{
    "age": int | None,
    "occupation": str | None,
    "income_band": str | None,
    "location": {
        "state": str | None
    }
}
```

**Behavior:**
- Never guesses values (uses `null` for missing info)
- Normalizes all languages into same schema
- Falls back to default profile on errors
- Latency target: < 2 seconds

### `generate_explanation(rule_output: dict, language: str = "en") -> str`

Generates human-friendly explanation from rule engine output.

**Parameters:**
- `rule_output`: Dict with keys:
  - `scheme`: str (scheme name)
  - `status`: str (`"eligible"` or `"not_eligible"`)
  - `reason`: str (technical reason)
- `language`: Language code (`en`, `hi`, `mr`)

**Returns:**
Simple explanation string in requested language (grade 6 reading level)

**Behavior:**
- NEVER modifies eligibility decision
- Only explains the decision
- Falls back to templates on errors
- No technical jargon

## ⚙️ Configuration

Edit `config.py` to customize:

- `MODEL_ID`: Bedrock model ID (default: Claude 3 Sonnet)
- `REGION`: AWS region (default: `us-east-1`)
- `TEMPERATURE`: Sampling temperature (default: `0.0` for deterministic output)
- `MAX_TOKENS`: Maximum response tokens (default: `1024`)
- `TIMEOUT_SECONDS`: Request timeout (default: `10`)

## 🛡️ Safety Guardrails

The LLM **never** makes eligibility decisions. Guardrails enforce this:

1. **Eligibility Decision Prevention:** LLM output is scanned for keywords like "eligible", "qualify", "पात्र". If found, fallback templates replace the output.
2. **JSON Validation:** Intent extraction must return valid JSON with the expected schema. Invalid output triggers fallback.
3. **Status Verification:** Explanation must not contradict the rule engine's status. Contradictory text triggers fallback.

Run `python guardrail_tests.py` to validate guardrails.

## 🔄 Fallback System

When Bedrock fails (timeout, error, etc.), the system automatically:

1. **Intent Extraction:** Returns default profile with all fields as `null`
2. **Explanation Generation:** Returns simple template explanation
3. **Error Handling:** Logs errors and continues gracefully

Fallback templates are defined in `fallback_templates.py` and support all three languages.

## 🏗️ Architecture Boundaries

**This Module (LLM Service):**
- ✅ Language understanding
- ✅ Intent extraction
- ✅ Explanation generation
- ✅ Multilingual support

**NOT This Module (Rule Engine):**
- ❌ Eligibility decisions
- ❌ Business logic
- ❌ Data persistence
- ❌ User authentication

The LLM module is designed to be a stateless service that integrates with a separate rule engine module.

---

## 🔌 Backend Integration

To integrate with Pranit's rule engine or your backend:

1. **Replace mock rule engine:**
   ```python
   from llm_service import extract_user_profile, generate_explanation
   from schema_adapter import normalize_rule_output
   # from your_backend import evaluate_rules  # Pranit's module

   profile = extract_user_profile(user_text, language)
   rule_output = evaluate_rules(profile)  # Your rule engine
   normalized = normalize_rule_output(rule_output)  # Prevents schema breakage
   explanation = generate_explanation(normalized, language)
   ```

2. **Use schema_adapter:** `normalize_rule_output(data)` ensures backend output matches expected schema (`scheme`, `status`, `reason`). Handles alternate key names and status values.

3. **Expected rule output schema:**
   ```python
   {"scheme": str, "status": "eligible"|"partially_eligible"|"not_eligible", "reason": str}
   ```

---

## 📝 Environment Variables

Copy `env.example` to `.env` and add keys when ready. Keys can be added later without code changes.

## 🐛 Troubleshooting

### "AccessDeniedException" or "Model not found"
- Ensure Bedrock model access is enabled in AWS console
- Check AWS credentials are correct
- Verify region supports Bedrock

### Timeout errors
- Increase `TIMEOUT_SECONDS` in `config.py`
- Check network connectivity
- Verify AWS service status

### Invalid JSON output
- System automatically falls back to templates
- Check prompt files are loaded correctly
- Review Bedrock model response format

### Import errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.8+)

## 📄 License

This module is part of the SamvaadAI hackathon project.

## 🤝 Contributing

This is a hackathon-ready module. For production use, consider:
- Adding retry logic with exponential backoff
- Implementing response caching
- Adding more comprehensive error handling
- Performance optimization for high throughput

---

**Built for SamvaadAI Hackathon** 🚀
