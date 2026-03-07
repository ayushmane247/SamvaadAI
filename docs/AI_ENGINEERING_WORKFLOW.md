# AI Engineering Workflow

**SamvaadAI — Conversational Eligibility Guidance System**

> Internal engineering document defining how AI tools are used across the SamvaadAI development lifecycle.

---

## 1. AI Tool Role Distribution

| AI Tool | Role | Boundary |
|---------|------|----------|
| **Claude Opus 4.6** | Architecture design, code review, edge case discovery, guardrail auditing | Development-time only. Never in production runtime. |
| **Claude Sonnet 4** (AWS Bedrock) | Explanation generation, language translation (en/hi/mr) | Production runtime only. Scoped to `llm_service/`. |
| **Cursor IDE** | Primary implementation environment. Code writing, refactoring, debugging. | Developer workstation only. |
| **Antigravity CLI** | Repository navigation, developer productivity, codebase exploration. | Developer workstation only. |

### Enforcement

- **No AI tool may access or modify the eligibility engine.** The `eligibility_engine/` module is a pure-Python deterministic system.
- Production LLM usage is restricted to `backend/llm_service/` and invoked exclusively through `BedrockClient`.
- All LLM interactions are logged with latency tracking (`[LLM_LATENCY]` prefix).

---

## 2. Development Workflow

```
┌──────────────────────────────────────────────────────────┐
│                   DEVELOPMENT PHASE                      │
│                                                          │
│  Cursor IDE ──→ Write/Refactor Code                      │
│  Claude Opus ──→ Architecture Review + Edge Cases        │
│  Antigravity ──→ Repo Navigation + Productivity          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                   REVIEW PHASE                           │
│                                                          │
│  Claude Opus ──→ Code Review                             │
│              ──→ Guardrail Audit (LLM boundary check)    │
│              ──→ Security Review (PII, input validation)  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                   PRODUCTION RUNTIME                     │
│                                                          │
│  Claude Sonnet 4 (Bedrock) ──→ Intent Extraction         │
│                             ──→ Explanation Generation   │
│                             ──→ Multilingual Response    │
│                                                          │
│  Eligibility Engine ──→ Deterministic Rule Evaluation    │
│  (NO AI INVOLVEMENT)                                     │
└──────────────────────────────────────────────────────────┘
```

### Workflow Steps

1. **Feature branch** created from `dev`
2. **Implementation** in Cursor IDE with Antigravity CLI support
3. **Architecture review** by Claude Opus (design patterns, contracts)
4. **Guardrail audit** by Claude Opus (verify LLM boundary enforcement)
5. **PR submitted** to `dev` with test evidence
6. **Merge to `main`** after review approval

---

## 3. Deterministic Architecture Rule

> **LLMs must NEVER decide eligibility.**

### What the Rule Engine Does

| Responsibility | Module | AI Involvement |
|---------------|--------|----------------|
| Parse eligibility criteria | `eligibility_engine/rule_parser.py` | ❌ None |
| Evaluate profile against rules | `eligibility_engine/engine.py` | ❌ None |
| Orchestrate evaluation | `orchestration/eligibility_service.py` | ❌ None |
| Load scheme datasets | `scheme_service/scheme_loader.py` | ❌ None |

### What the LLM Service Does

| Responsibility | Module | AI Involvement |
|---------------|--------|----------------|
| Extract user attributes from natural language | `llm_service/llm_service.py` | ✅ Claude Sonnet |
| Generate human-friendly explanations | `llm_service/llm_service.py` | ✅ Claude Sonnet |
| Multilingual responses (en, hi, mr) | `llm_service/fallback_templates.py` | ✅ Claude Sonnet with template fallback |

### Data Flow Guarantee

```
User Input (NL) ──→ LLM: Extract Attributes ──→ Structured Profile
                                                       │
                                                       ▼
                                              Rule Engine: Evaluate
                                                       │
                                                       ▼
                                              Deterministic Result
                                                       │
                                                       ▼
                                      LLM: Explain Result (read-only)
                                                       │
                                                       ▼
                                              User-Friendly Response
```

**The LLM never sees, modifies, or influences the eligibility decision.**

---

## 4. Guardrail Strategy

### Runtime Guardrails (Production)

| Guardrail | Implementation | Location |
|-----------|---------------|----------|
| **Eligibility keyword detection** | Regex scan for eligibility-related terms in LLM output | `LLMService._check_eligibility_guardrail()` |
| **Status contradiction check** | Verify LLM explanation doesn't contradict engine decision | `LLMService.generate_explanation()` L314-317 |
| **Profile schema validation** | Validate extracted profile matches expected schema | `LLMService._validate_profile_schema()` |
| **JSON output validation** | Validate LLM returns parseable JSON for extraction | `LLMService._extract_json_from_response()` |
| **Fallback templates** | Deterministic templates when LLM fails | `fallback_templates.py` (all 3 languages) |
| **Session field whitelisting** | Only `structured_profile`, `conversation_state`, `evaluation_result` updatable | `SessionService.update_session()` |

### Development-Time Guardrails

| Guardrail | Implementation |
|-----------|---------------|
| **Import boundary audit** | Claude Opus verifies `eligibility_engine/` has zero LLM imports |
| **Data flow audit** | Claude Opus verifies LLM output never feeds into `evaluate()` as a decision |
| **PII leakage review** | Claude Opus checks error handlers strip internal details |
| **Prompt injection review** | Claude Opus reviews prompt templates for injection vectors |

### Failure Modes

| Failure | System Behavior |
|---------|----------------|
| LLM times out | Return `fallback_templates` response |
| LLM returns invalid JSON | Return `get_default_profile()` |
| LLM includes eligibility language | Guardrail triggers → fallback template |
| LLM contradicts engine decision | Guardrail triggers → fallback explanation |
| S3 unavailable | Serve stale cache if available |
| Bedrock unavailable | Full fallback to templates (no LLM dependency for eligibility) |

---

## 5. Token Cost Control Strategy

### Model Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | Claude Sonnet 4 | Cost-optimized for language tasks |
| Temperature | `0.0` | Deterministic output, reduces variance |
| Max Tokens | `1024` | Sufficient for extraction/explanation |
| Timeout | `10s` | Fail fast, use fallbacks |
| Retries | `2` (standard mode) | Limit cost from retry storms |

### Cost Controls

| Control | Implementation |
|---------|---------------|
| **Two-call maximum** | Each user turn invokes at most 2 LLM calls (extraction + explanation) |
| **Prompt templates** | Externalized in `prompts/` directory, version-controlled |
| **Fallback-first design** | Templates handle all failure modes without LLM re-invocation |
| **No LLM for eligibility** | Rule engine is zero-cost per evaluation |
| **Scheme caching** | 5-minute TTL cache avoids per-request S3 fetches |
| **Cold-start preload** | Schemes loaded at Lambda init, not per-request |
| **Latency tracking** | `[LLM_LATENCY]` logs enable cost/performance correlation |

### Monitoring

- Track `intent_extraction` and `explanation_generation` latency separately
- Alert on evaluation latency exceeding `EVALUATION_LATENCY_THRESHOLD_MS` (2000ms)
- Log all LLM fallback activations for cost-avoidance metrics

---

## 6. AI Development Best Practices

### For Production LLM Usage

1. **Never trust LLM output for decisions.** Always validate, parse, and schema-check.
2. **Always have a fallback.** Every LLM call must have a deterministic fallback path.
3. **Log everything.** Every LLM invocation must log: task type, latency, success/failure.
4. **Externalize prompts.** Prompts live in `prompts/` as text files, not inline strings.
5. **Temperature zero.** Use `0.0` for all structured extraction tasks.
6. **Schema validation.** Validate LLM JSON output against expected schema before use.

### For AI-Assisted Development

1. **Claude Opus for architecture, not implementation.** Use it for review and design, not bulk code generation.
2. **Guardrail audits on every PR.** Before merging, verify LLM boundary is intact.
3. **Test the boundary.** Integration tests must verify `eligibility_engine/` never imports from `llm_service/`.
4. **Document AI decisions.** When an AI tool influences a design choice, note it in the PR.
5. **Version prompts.** Treat prompt files as production code — review and version them.

### Anti-Patterns (Prohibited)

| Anti-Pattern | Why It's Prohibited |
|-------------|-------------------|
| LLM deciding eligibility | Violates core architecture rule |
| Inline prompt strings | Prevents prompt versioning and review |
| Missing fallback for LLM call | System fails when Bedrock is unavailable |
| Logging PII in error messages | Privacy violation |
| LLM retry without backoff | Cost explosion risk |
| Trusting LLM JSON without validation | Integration breakage risk |

---

## 7. SamvaadAI AI Org Chart

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI TOOL ORGANIZATION                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              DEVELOPMENT-TIME AI                          │  │
│  │                                                           │  │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │  Claude Opus 4.6│  │  Cursor IDE  │  │ Antigravity │  │  │
│  │  │                 │  │              │  │    CLI      │  │  │
│  │  │ • Architecture  │  │ • Write code │  │ • Navigate  │  │  │
│  │  │ • Code review   │  │ • Refactor   │  │ • Search    │  │  │
│  │  │ • Edge cases    │  │ • Debug      │  │ • Explore   │  │  │
│  │  │ • Guardrail     │  │              │  │             │  │  │
│  │  │   auditing      │  │              │  │             │  │  │
│  │  └─────────────────┘  └──────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              PRODUCTION RUNTIME AI                        │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Claude Sonnet 4 (AWS Bedrock)                      │  │  │
│  │  │                                                     │  │  │
│  │  │  Permitted:                                         │  │  │
│  │  │  • Extract attributes from natural language         │  │  │
│  │  │  • Generate explanations of rule engine decisions   │  │  │
│  │  │  • Translate responses (English, Hindi, Marathi)    │  │  │
│  │  │                                                     │  │  │
│  │  │  Prohibited:                                        │  │  │
│  │  │  ✗ Eligibility decisions                            │  │  │
│  │  │  ✗ Rule evaluation                                  │  │  │
│  │  │  ✗ Scheme matching                                  │  │  │
│  │  │  ✗ Profile scoring                                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              ZERO-AI ZONE (Deterministic Core)            │  │
│  │                                                           │  │
│  │  eligibility_engine/   — Rule parsing + evaluation        │  │
│  │  orchestration/        — Service coordination             │  │
│  │  scheme_service/       — S3 data loading + caching        │  │
│  │  session_store/        — DynamoDB persistence              │  │
│  │                                                           │  │
│  │  ⚠ No AI tool may modify or influence these modules.      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Version:** 1.0  
**Last Updated:** March 2026  
**Owner:** SamvaadAI Core Team
