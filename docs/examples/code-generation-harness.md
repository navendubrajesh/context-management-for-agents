# Code Generation Harness + Eval Gate (CM-608)

This guide shows how to wire the `examples/code-generation-harness` into CI using eval-as-a-service.

## Local harness

```bash
pip install -e runtime/core -e runtime/sdk-python
python -m pytest examples/code-generation-harness/tests/ -q
python examples/code-generation-harness/harness.py
```

## Eval-as-a-service gate

The hosted API exposes `POST /eval/run` for deterministic checks and optional LLM-as-judge scoring.

Sample GitHub Action step:

```yaml
- name: Codegen harness + eval gate
  run: |
    python -m pytest examples/code-generation-harness/tests/ -q
    uvicorn app:app --app-dir runtime/api --host 127.0.0.1 --port 8080 &
    sleep 3
    python examples/code-generation-harness/harness.py --eval-url http://127.0.0.1:8080/eval/run
```

See `.github/workflows/codegen-eval-gate.yml` for a complete workflow template.
