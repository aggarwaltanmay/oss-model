# OSS Model Deployment Repository

This repository contains scripts, configurations, and utilities to deploy an open‑source large language model (Qwen2.5‑0.5B‑Instruct) on multiple platforms, with observability, guardrails, memory, and tool‑use capabilities.

## Directory Layout

- `model/` – Model download and conversion scripts.
- `deploy/` – Platform‑specific deployment configs and Dockerfiles.
- `infra/` – Infrastructure as code (Terraform / Pulumi).
- `observability/` – OpenTelemetry instrumentation and Grafana/Loki dashboards.
- `guardrails/` – Prompt templates and moderation wrappers.
- `memory/` – In‑memory cache and optional vector store integration.
- `tools/` – Abstract tool definitions and concrete implementations.
- `evals/` – Evaluation scripts and datasets.
- `cost_latency/` – Benchmarking utilities and cost‑latency table generator.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Follow the deployment guides in `deploy/` for each target platform.
3. Run the evaluation suite:
   ```bash
   python evals/run_benchmarks.py
   ```

For detailed instructions, see the platform‑specific README files inside `deploy/`.
