import os

import requests
import json

url = "http://localhost:8000/api/v1/ideation/generate"
# Token intentionally not committed. Export SME_TOOLKIT_TOKEN (see get_token.py).
token = os.environ.get("SME_TOOLKIT_TOKEN", "")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

payload = {
    "action": "brainstorm",
    "topic": "Improving customer retention",
    "context": {"business_type": "e-commerce", "current_metrics": {"retention_rate": "45%"}},
    "template": "scamper",
    "industry": "e-commerce",
    "target_audience": "online shoppers",
    "constraints": ["Budget-friendly", "Quick implementation"],
    "innovation_level": "disruptive",
    "quantity": 3
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
