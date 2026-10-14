import os

import requests
import json

url = "http://localhost:8000/api/v1/ideation/generate"
# Token intentionally not committed. Export SME_TOOLKIT_TOKEN (see get_token.py).
token = os.environ.get("SME_TOOLKIT_TOKEN", "")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

templates = ["scamper", "mind_map", "swot", "blue_ocean", "lean_startup", "design_thinking", "first_principles", "reverse_engineering"]

for template in templates:
    payload = {
        "action": "brainstorm",
        "topic": "Improving customer retention",
        "context": {"business_type": "e-commerce", "current_metrics": {"retention_rate": "45%"}},
        "template": template,
        "industry": "e-commerce",
        "target_audience": "online shoppers",
        "constraints": ["Budget-friendly", "Quick implementation"],
        "innovation_level": "disruptive",
        "quantity": 3
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"\n=== Testing template: {template} ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Action: {result.get('action')}")
            ideas = result.get('ideas')
            print(f"Ideas generated: {len(ideas) if ideas else 0}")
            insights = result.get('insights')
            print(f"Insights: {len(insights) if insights else 0}")
            recommendations = result.get('recommendations')
            print(f"Recommendations: {len(recommendations) if recommendations else 0}")
            print(f"Template used: {result.get('template_used')}")
            if template in ['first_principles', 'reverse_engineering', 'design_thinking']:
                print(f"Debug - Ideas type: {type(ideas)}, value: {ideas}")
                print(f"Debug - Raw ideas count: {len(result.get('ideas', []))}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing template {template}: {e}")
