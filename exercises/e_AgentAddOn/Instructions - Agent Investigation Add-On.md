# Agent Investigation Add-On (Optional)
An optional add-on, separate from the core 4 exercises. It demonstrates building and tracing an agent in Domino: a small agent investigates a transaction the fraud model already flagged, calls two mock lookup tools, and gives a plain-language recommendation. Every run produces a real, inspectable trace using Domino's GenAI tracing SDK.

## Prerequisites

This add-on calls an LLM, so unlike the core exercises it needs two things in place:

- [ ] The `anthropic` package installed in the compute environment (add `RUN pip install --no-cache-dir anthropic` to the environment's Docker instructions and rebuild).
- [ ] An `ANTHROPIC_API_KEY` set as a project environment variable (Project → Settings → Environment Variables). Never commit the key to the repo.

## Exercise Instructions

1. Publish `exercises/e_AgentAddOn/app.sh` as an Agent (Apps & Agents → Publish Agent, Source: Project files).
2. Open the published agent, pick a flagged transaction, and click "Investigate".
3. Review the summary and recommendation (ESCALATE / MONITOR / CLEAR).
4. Go to the agent's **Traces** tab and walk through the span tree: the LLM calls, the two tool calls, and the evaluator score attached to the top-level span.

To run it from a terminal instead of as an agent: `python exercises/e_AgentAddOn/agent.py` investigates both sample transactions and logs a development run under Experiments → `fraud-investigation-agent`.

This concludes the optional "Agent Investigation" add-on.

## New Domino Concepts

**GenAI Tracing:**
> Domino's GenAI tracing captures every LLM call, tool call, and intermediate step an agent takes as a structured trace — token usage, latency, and evaluator scores included — so agent behavior is as inspectable and auditable as a traditional ML experiment run.

## Notes

- The two tools (`check_merchant_risk_history`, `check_ip_reputation`) are deliberately mocked and deterministic — no external system is called, so the demo is self-contained and fast.
- `init_tracing()` at the top of `agent.py` is what routes traces to the agent's own experiment when running as a published Agent. Don't call `mlflow.set_experiment()` after it in that path, or traces will be logged elsewhere.
