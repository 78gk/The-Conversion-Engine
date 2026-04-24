import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("ERROR: OPENROUTER_API_KEY not found in .env")
    exit(1)

print(f"Key loaded: {api_key[:12]}...{api_key[-4:]}")

# /auth/key — only works for personal keys, not org-provisioned
try:
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/auth/key',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())['data']
        print(f"Key Label  : {data.get('label')}")
        print(f"Credits Used: ${data.get('usage', 0):.4f}")
        limit = data.get('limit')
        print(f"Credit Limit: ${limit if limit is not None else 'No limit set'}")
except urllib.error.HTTPError as e:
    if e.code == 401:
        print("Note: /auth/key returned 401 — org-provisioned keys cannot query their own metadata.")
        print("Testing with a live model call instead...")
    else:
        print(f"Unexpected error: {e}")

# Live call test — tiny prompt, cheapest free model
print("\n--- Live call test ---")
payload = json.dumps({
    "model": "google/gemma-3-4b-it:free",
    "messages": [{"role": "user", "content": "Reply with just: OK"}],
    "max_tokens": 5
}).encode()

req2 = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    data=payload,
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
)
try:
    with urllib.request.urlopen(req2) as response:
        result = json.loads(response.read())
        reply = result['choices'][0]['message']['content']
        model_used = result.get('model', 'unknown')
        usage = result.get('usage', {})
        print(f"Status      : KEY WORKS")
        print(f"Model       : {model_used}")
        print(f"Reply       : {reply.strip()}")
        print(f"Tokens used : {usage.get('total_tokens', '?')}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"FAILED: {e.code} — {body}")
