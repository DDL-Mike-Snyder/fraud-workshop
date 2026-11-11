#!/usr/bin/env bash
# Starts the two open models as OpenAI-compatible vLLM servers on this machine's GPU.
#   :8000  txn-generator  Granite-3.3-8B-Instruct (tool calling)  -> generator agent
#   :8001  fraud-llm      fine-tuned Granite-3.3-2B               -> fraud-scoring agent
# Called by the repo-root app.sh. Runs in the background so the app starts immediately; the
# models become ready after a few minutes. Weights are cached in the project dataset.
set -uo pipefail

# Domino-hosted projects: <datasets>/local/<project>. Git-based projects: <datasets>/<project>/<user>.
if [ "${DOMINO_IS_GIT_BASED:-}" = "true" ]; then
  DS="${DOMINO_DATASETS_DIR:-/domino/datasets}/${DOMINO_PROJECT_NAME:-fraud-workshop}/${DOMINO_USER_NAME:-}"
else
  DS="${DOMINO_DATASETS_DIR:-/domino/datasets}/local/${DOMINO_PROJECT_NAME:-fraud-workshop}"
fi
export HF_HOME="${HF_HOME:-$DS/hf_cache}"
# The image has no CUDA toolkit (nvcc), so avoid FlashInfer kernels that compile at runtime.
export VLLM_USE_FLASHINFER_SAMPLER=0
GEN_MODEL="${GENERATOR_MODEL:-ibm-granite/granite-3.3-8b-instruct}"
FRAUD_MODEL_DIR="${FRAUD_MODEL_DIR:-$DS/models/fraud-llm}"
LOG=/tmp/llm-logs; mkdir -p "$HF_HOME" "$LOG"

if ! command -v vllm >/dev/null || ! nvidia-smi >/dev/null 2>&1; then
  echo "serve_llms: no GPU or no vllm in this environment; skipping LLM servers."
  exit 0
fi

# Size the two servers to the card. >=40 GB: bf16 generator. Smaller (e.g. 24 GB): FP8 generator.
MEM_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
if [ "${MEM_MIB:-0}" -ge 40000 ]; then
  GEN_MEM="${GEN_GPU_MEM:-0.55}"; FRAUD_MEM="${FRAUD_GPU_MEM:-0.25}"; GEN_QUANT="${GEN_QUANT:-}"
else
  GEN_MEM="${GEN_GPU_MEM:-0.55}"; FRAUD_MEM="${FRAUD_GPU_MEM:-0.32}"; GEN_QUANT="${GEN_QUANT:-fp8}"
fi
echo "serve_llms: GPU ${MEM_MIB} MiB, generator mem=$GEN_MEM quant=${GEN_QUANT:-none}, fraud mem=$FRAUD_MEM"

pkill -f "vllm serve" 2>/dev/null || true
(
  vllm serve "$GEN_MODEL" --served-model-name txn-generator --port 8000 \
    --gpu-memory-utilization "$GEN_MEM" --max-model-len 8192 ${GEN_QUANT:+--quantization "$GEN_QUANT"} \
    --enable-auto-tool-choice --tool-call-parser granite > "$LOG/generator.log" 2>&1 &
  # Start the second server only after the first has claimed its memory, so the two
  # startup memory checks do not collide.
  for _ in $(seq 1 180); do curl -sf localhost:8000/health >/dev/null && break; sleep 5; done
  if [ -d "$FRAUD_MODEL_DIR" ]; then
    vllm serve "$FRAUD_MODEL_DIR" --served-model-name fraud-llm --port 8001 \
      --gpu-memory-utilization "$FRAUD_MEM" --max-model-len 1024 --enforce-eager > "$LOG/fraud.log" 2>&1 &
  else
    echo "serve_llms: $FRAUD_MODEL_DIR not found. Run finetune_fraud_llm.py as a Job first."
  fi
  # Smoke test: one tool-calling request and one fraud score, so the app log shows both work.
  for _ in $(seq 1 120); do curl -sf localhost:8001/health >/dev/null && break; sleep 5; done
  echo "SMOKE generator: $(curl -s localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"txn-generator","messages":[{"role":"user","content":"Make 5 transactions, 40% fraud."}],"tools":[{"type":"function","function":{"name":"generate_transactions","description":"Simulate transactions","parameters":{"type":"object","properties":{"n":{"type":"integer"},"fraud_rate":{"type":"number"}},"required":["n"]}}}],"max_tokens":200,"temperature":0}' | head -c 700)"
  echo "SMOKE fraud: $(curl -s localhost:8001/v1/completions -H 'Content-Type: application/json' -d '{"model":"fraud-llm","prompt":"Classify this card transaction as fraud (1) or legitimate (0).\nAmount: 900.00\nlabel=","max_tokens":1,"temperature":0,"logprobs":5}' | head -c 700)"
  (cd "${DOMINO_WORKING_DIR:-/mnt/code}" && python exercises/f_OpenModelAgents/smoke_test.py 2>&1 | grep -E "^E2E|Error|Traceback|^ " | head -40)
  wait
) > "$LOG/launcher.log" 2>&1 &
# Mirror the server logs into this process's output so they show in the app's log view.
touch "$LOG/generator.log" "$LOG/fraud.log" "$LOG/launcher.log"
tail -n 0 -F "$LOG/generator.log" "$LOG/fraud.log" "$LOG/launcher.log" &
echo "serve_llms: servers starting in background (logs in $LOG)."
