import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/auth/key', 
    headers={'Authorization': f'Bearer {api_key}'}
)

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())['data']
    print(f"Key Label: {data.get('label')}")
    print(f"Credits Used: ${data.get('usage', 0):.4f}")
    limit = data.get('limit')
    print(f"Credit Limit: ${limit if limit is not None else 'No limit set'}")
