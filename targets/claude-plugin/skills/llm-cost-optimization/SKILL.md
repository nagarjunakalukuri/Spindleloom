---
name: llm-cost-optimization
description: Four levers for reducing LLM API spend without degrading quality — model selection/routing, token efficiency, prompt caching, and batching. Code examples for the Anthropic API. Pricing-aware model routing pattern, per-feature cost instrumentation, and the cost-vs-quality trade-off framework. For ai-orchestrator and ai-eval agents.
---


LLM API costs compound fast: a feature that's cheap in demo becomes expensive at scale. The four levers below can typically reduce spend by 60–90% without meaningful quality loss. Apply them in order — routing and caching give the biggest wins.

---

## Lever 1 — Model selection and routing

**Rule:** use the cheapest model that meets the quality bar for each task.

| Task type | Model tier | Rationale |
|---|---|---|
| Structured extraction, classification, simple rewrites | Small / fast (Haiku-class) | Near-deterministic; quality parity with larger |
| RAG retrieval + grounding, code review, summarization | Mid (Sonnet-class) | Judgment required; fast model misses edge cases |
| Complex reasoning, architecture, long-context synthesis | Large (Opus-class) | Reserve for genuinely hard tasks only |
| Evals / LLM-as-judge | Mid, same or larger than the model under test | Judge must be at least as capable as the model it judges |

**Pricing-aware router pattern (Python):**

```python
from anthropic import Anthropic

TASK_MODEL_MAP = {
    "extract":    "claude-haiku-4-5-20251001",      # cheap + fast
    "review":     "claude-sonnet-4-6",              # mid-tier
    "reason":     "claude-opus-4-8",                # expensive — use sparingly
}

def call(task: str, prompt: str, **kwargs):
    model = TASK_MODEL_MAP.get(task, "claude-sonnet-4-6")
    client = Anthropic()
    return client.messages.create(model=model, messages=[{"role": "user", "content": prompt}], **kwargs)
```

**Anti-pattern:** defaulting every call to the largest model "to be safe" — this is 5–20× the cost of the right-sized model on the same task.

---

## Lever 2 — Token efficiency

### Prompt compression
- Remove boilerplate and repeated context the model doesn't need to see each call.
- Use a system prompt for stable instructions; use the user turn only for the variable part.
- Prefer structured input formats (JSON/YAML) over prose narration — shorter and more reliable.

### Output sizing
Request structured output (`max_tokens` + JSON schema tool) to prevent over-generation:

```python
import anthropic, json

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,               # cap output — most extractions need <200 tokens
    tools=[{
        "name": "extract_fields",
        "description": "Extract the requested fields",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "status": {"type": "string", "enum": ["open", "closed", "pending"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["title", "status"]
        }
    }],
    tool_choice={"type": "tool", "name": "extract_fields"},
    messages=[{"role": "user", "content": "Extract from: " + document}]
)
fields = json.loads(response.content[0].input)
```

### Context management
- For multi-turn agents, summarize earlier turns instead of passing the full history (`/summarize` pattern).
- Pass only the document sections relevant to the current step, not the full document.
- Use `count_tokens` before expensive calls to catch runaway context early.

```python
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": my_prompt}]
)
if token_count.input_tokens > 50_000:
    raise ValueError(f"Prompt too large: {token_count.input_tokens} tokens — summarize first")
```

---

## Lever 3 — Prompt caching

Cache stable prompt sections (system prompts, reference documents, few-shot examples) so they're only charged at 10% of normal input cost on subsequent calls.

**When to use:** system prompt > 1 024 tokens; long reference document reused across calls; large few-shot block repeated in a session.

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """
You are a senior code reviewer. Apply these standards... [2 000 tokens of standards doc]
"""

def review_file(code: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}   # cache this section
        }],
        messages=[{"role": "user", "content": f"Review this:\n\n{code}"}]
    )
    # cache_read_input_tokens in response.usage shows cache hits
    return response.content[0].text
```

**Cache hit tracking:**
```python
usage = response.usage
print(f"input: {usage.input_tokens}, "
      f"cache_creation: {usage.cache_creation_input_tokens}, "
      f"cache_read: {usage.cache_read_input_tokens}")
# cache_read tokens cost ~10% of normal input — verify the hit rate in your metrics
```

Cache TTL: 5 minutes (reset on each hit). For longer sessions, re-send the cache_control block every ~4 minutes to keep it warm.

---

## Lever 4 — Batching

Use the Batch API for workloads that don't need an immediate response (evals, nightly processing, bulk analysis). Batch API charges at ~50% of normal input cost.

```python
import anthropic, json

client = anthropic.Anthropic()

# Build a batch of requests (max 10 000 per batch, max 32 MB)
requests = [
    {
        "custom_id": f"review-{i}",
        "params": {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": f"Classify severity: {ticket['text']}"}]
        }
    }
    for i, ticket in enumerate(support_tickets)
]

batch = client.messages.batches.create(requests=requests)
print(f"Batch {batch.id} submitted: {len(requests)} requests")

# Poll until done (or use a webhook); typical completion: minutes to hours
import time
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    time.sleep(60)

# Stream results
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(result.custom_id, result.result.message.content[0].text)
```

**Rule:** use Batch API whenever latency > 1 h is acceptable — eval runs, nightly summaries, bulk backlog classification.

---

## Per-feature cost instrumentation

Track actual spend per feature from day one, not just total API spend:

```python
import time
from dataclasses import dataclass

@dataclass
class CallRecord:
    feature: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    latency_ms: float

COST_PER_MTok = {
    "claude-haiku-4-5-20251001": {"input": 0.80,  "output": 4.00,  "cache_read": 0.08},
    "claude-sonnet-4-6":         {"input": 3.00,  "output": 15.00, "cache_read": 0.30},
    "claude-opus-4-8":           {"input": 15.00, "output": 75.00, "cache_read": 1.50},
}

def cost_usd(record: CallRecord) -> float:
    rates = COST_PER_MTok.get(record.model, COST_PER_MTok["claude-sonnet-4-6"])
    return (
        record.input_tokens      * rates["input"]      / 1_000_000 +
        record.output_tokens     * rates["output"]     / 1_000_000 +
        record.cache_read_tokens * rates["cache_read"] / 1_000_000
    )
```

**Emit to your metrics system** (DataDog, Prometheus, CloudWatch) with dimensions: `feature`, `model`, `cache_hit` — so you can answer "how much does our RAG feature cost per 1 000 queries?"

---

## Cost-vs-quality trade-off checklist

Before accepting a cost-optimization change, verify:
- [ ] Quality benchmark ran before and after — actual scores, not assumed
- [ ] Smaller model tested on the edge cases (failure modes), not just the happy path
- [ ] Cache hit rate measured (aim for > 70% on sessions > 5 calls with a stable system prompt)
- [ ] Batch latency acceptable for the feature's UX contract (batch ≠ real-time)
- [ ] Per-feature cost metric wired in CI or a dashboard — not just total spend

---

## Style rules
- Size the model to the task; never default to the largest "to be safe."
- Cache system prompts and reference documents that repeat across calls.
- Batch any workload where latency > 1 h is acceptable.
- Instrument per-feature cost from day one — aggregate spend hides regressions.
- Verify quality after optimization; cost savings that break the feature aren't savings.
