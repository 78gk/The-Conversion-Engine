"""Cross-platform tau2-bench runner. Works on Windows without bash/WSL."""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAU2_DIR = ROOT / "tau2-bench"

# Load .env
env_path = ROOT / ".env"
env = os.environ.copy()
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"')

agent_llm = sys.argv[1] if len(sys.argv) > 1 else "gemini/gemini-2.0-flash"
num_tasks = sys.argv[2] if len(sys.argv) > 2 else "30"

# Use same provider as agent for user sim to avoid cross-provider key issues
user_llm = agent_llm

print(f"Agent LLM : {agent_llm}")
print(f"User  LLM : {user_llm}")
print(f"Tasks     : {num_tasks}")

tau2_exe = TAU2_DIR / ".venv" / "Scripts" / "tau2.exe"

cmd = [
    str(tau2_exe),
    "run",
    "--domain", "retail",
    "--agent", "llm_agent",
    "--agent-llm", agent_llm,
    "--agent-llm-args", '{"temperature": 0}',
    "--user-llm", user_llm,
    "--num-tasks", str(num_tasks),
    "--num-trials", "1",
    "--max-concurrency", "1",
    "--auto-resume",
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd, cwd=TAU2_DIR, env=env)
sys.exit(result.returncode)
