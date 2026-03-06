# SamvaadAI LLM Module — Overview for Judges

## Purpose

This module provides **language understanding** and **explanation generation** for a government scheme eligibility assistant. It supports English, Hindi, and Marathi, and is designed to integrate with a separate, deterministic rule engine that makes eligibility decisions.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SAMVADAI PIPELINE                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   USER INPUT          LLM MODULE              RULE ENGINE         LLM MODULE │
│   (en/hi/mr)                                                                  │
│        │                   │                        │                   │    │
│        ▼                   ▼                        ▼                   ▼    │
│   ┌─────────┐      ┌───────────────┐       ┌──────────────┐    ┌──────────┐  │
│   │ "I am   │─────▶│ Extract       │──────▶│ Evaluate     │───▶│ Explain  │  │
│   │ farmer" │      │ Profile       │       │ Rules        │    │ Result   │  │
│   └─────────┘      │ (understanding)│       │ (deterministic)  │ (human   │  │
│                    └───────────────┘       └──────────────┘    │ language)│  │
│                           │                        │                   │    │
│                           │                        │                   │    │
│                    LLM/Bedrock              NO AI/LLM            LLM/Bedrock │
│                    or fallback                                       or      │
│                                                                    fallback  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Responsibilities

| This Module Does | This Module Does Not |
|------------------|----------------------|
| Extract structured profile from user text (age, occupation, income, location) | Make eligibility decisions |
| Generate simple, human-friendly explanations in 3 languages | Store user data |
| Fall back to templates when LLM is unavailable | Use a database |
| Validate output and enforce safety guardrails | Change or override rule engine decisions |

---

## Why LLM Is Not Used for Decision-Making

1. **Determinism** — Eligibility must be auditable and reproducible.
2. **Safety** — LLMs can hallucinate; deterministic rules are predictable.
3. **Compliance** — Government schemes need traceable, explicit logic.
4. **Reliability** — The system keeps working when Bedrock is down.

Eligibility is always decided by the **rule engine**, never by the LLM.

---

## Integration Flow

```
1. User sends text (e.g., "मैं किसान हूं") + language preference
2. LLM extracts profile → {age, occupation, income_band, location}
3. Rule engine evaluates profile → {scheme, status, reason}
4. LLM explains the result in the chosen language
5. Response returned to user
```

The module is **stateless** and **integratable**: backend sends profile + rule output, module returns explanation.

---

## Demo Capabilities

- **Full pipeline demo** — `python demo_run.py` (works without AWS)
- **3 languages** — English, Hindi, Marathi
- **3 demo flows** — English farmer, Hindi teacher, Marathi user
- **Fallback mode** — Uses templates when Bedrock is unavailable

---

## Safety Guardrails

- **Eligibility-blocking** — LLM output is scanned for eligibility keywords; if found, fallback templates are used.
- **Schema checks** — Intent extraction must return valid JSON with the expected structure.
- **Status checks** — Explanations must not contradict the rule engine’s status.

---

## Hackathon-Ready Summary

This module is designed for a hackathon: it runs without AWS, uses clear fallbacks, and keeps LLM usage limited to understanding and explanation. Eligibility logic stays in the rule engine for reliability and compliance.
