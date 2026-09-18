# AI / LLM targets

Mock LLM security challenges. **No model is hosted** -- each target is a
deterministic Flask app that simulates an LLM application's behaviour, so
defeating the simulated guardrail is the challenge. Reproducible, no GPU, no
API keys. Host ports: **8700s**.

```bash
./bench list --domain ai
./bench up aq-ai-ben1
```

## How they run

`native-python` Flask apps with rule-based logic standing in for a model. They
map to the **OWASP Top 10 for LLM Applications**:

- **LLM01 Prompt Injection** -- bypass an input guardrail to leak a hidden
  system prompt (see `aq-ai-ben1`).
- **LLM02 Insecure Output Handling** -- model output rendered unsafely (XSS).
- **LLM06 Sensitive Information Disclosure** -- a mock RAG leaks a confidential
  chunk.
- **RAG poisoning / LLM08 Excessive Agency** -- planted documents or a tricked
  mock "agent".

## Building one

Write the "assistant" as deterministic logic: a hidden secret, a simulated
guardrail (blocklist / regex / template), and an intended bypass. Never call a
real model. See [../for-researchers.md](../for-researchers.md) for design and
[../for-developers.md](../for-developers.md) for packaging.
