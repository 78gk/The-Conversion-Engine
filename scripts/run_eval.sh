#!/usr/bin/env bash
# Run tau2-bench retail eval with environment from .env
# Usage: bash scripts/run_eval.sh [model] [num_tasks]
#   model     default: openrouter/anthropic/claude-3.5-sonnet
#   num_tasks default: 30

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
TAU2_DIR="$ROOT/tau2-bench"

# Load .env
if [ -f "$ROOT/.env" ]; then
  set -a
  source "$ROOT/.env"
  set +a
fi

AGENT_LLM="${1:-openrouter/anthropic/claude-3.5-sonnet}"
NUM_TASKS="${2:-30}"
USER_LLM="${USER_LLM_MODEL:-openrouter/meta-llama/llama-3.3-70b-instruct}"

echo "Agent LLM : $AGENT_LLM"
echo "User  LLM : $USER_LLM"
echo "Tasks     : $NUM_TASKS"
echo "Starting tau2 run..."

cd "$TAU2_DIR"
.venv/Scripts/tau2.exe run \
  --domain retail \
  --agent llm_agent \
  --agent-llm "$AGENT_LLM" \
  --agent-llm-args '{"temperature": 0}' \
  --user-llm "$USER_LLM" \
  --num-tasks "$NUM_TASKS" \
  --num-trials 1 \
  --max-concurrency 4 \
  --auto-resume
