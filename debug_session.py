from cowrie.adaptive.session_analyzer import SessionAnalyzer
from cowrie.adaptive.rule_based_analyzer import RuleBasedAnalyzer
import json

s = SessionAnalyzer()
sid = 'ddbf67bab2f6'
# Hack to focus on this session
events = []
with open(s.log_path, 'r') as f:
    for line in f:
        try:
            ev = json.loads(line)
            if ev.get('session') == sid:
                events.append(ev)
        except: pass

print(f"Loaded {len(events)} events for {sid}")
summary = s.summarize_session({'session_id': sid, 'events': events})
print(f"Summary commands: {summary['commands']}")

rb = RuleBasedAnalyzer()
res = rb.analyze(summary)
print(f"RB Analysis: Score={res['risk_score']}, Matches={res['rule_matches']}")
