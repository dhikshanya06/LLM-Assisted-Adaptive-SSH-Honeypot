import json
import os

POLICY_FILE = "var/lib/cowrie/session_policies.json"
SID = "ddbf67bab2f6"

if os.path.exists(POLICY_FILE):
    with open(POLICY_FILE, 'r') as f:
        data = json.load(f)
else:
    data = {}

data[SID] = {
    "level": 3,
    "reasoning": {
        "manual_override": "Unblocking user while controller processes backlog",
        "rule_based": {"risk_score": 34.0, "intent": "Highly Malicious"}
    }
}

with open(POLICY_FILE, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Patched {SID} to Level 3")
