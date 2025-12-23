#!/home/dhikshanya06/cowrie/cowrie-env/bin/python3
import json
import time
import datetime
import os
import sys

# Add the adaptive directory to path so it can find its siblings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from twisted.internet import reactor, task, defer
    from session_analyzer import SessionAnalyzer
    from rule_based_analyzer import RuleBasedAnalyzer
    from llm_analyzer import LLMAnalyzer
    from adaptive_controller import AdaptiveController
except ImportError as e:
    print("\n[!] Error: Missing dependencies (Twisted, etc).")
    print(f"    Details: {e}")
    print("\n[!] PLEASE RUN WITH THE COWRIE VIRTUAL ENVIRONMENT:")
    print("    /home/dhikshanya06/cowrie/cowrie-env/bin/python3 live_adaptive_controller.py")
    print("\n    Or use the helper script:")
    print("    ./run_live_controller.sh\n")
    sys.exit(1)

# Determine the project root relative to this script
# Script is in src/cowrie/adaptive
# Root is 3 levels up: cowrie/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
POLICY_FILE = os.path.join(PROJECT_ROOT, 'var', 'lib', 'cowrie', 'session_policies.json')

class LiveAdaptiveController:
    def __init__(self):
        self.s_analyzer = SessionAnalyzer()
        self.rb_analyzer = RuleBasedAnalyzer()
        self.llm_analyzer = LLMAnalyzer()
        self.controller = AdaptiveController(self.rb_analyzer, self.llm_analyzer)
        self.policies = {}
        self.load_policies()

    def load_policies(self):
        if os.path.exists(POLICY_FILE):
            try:
                with open(POLICY_FILE, 'r') as f:
                    self.policies = json.load(f)
            except Exception:
                self.policies = {}

    def save_policies(self):
        # Ensure directory exists
        policy_dir = os.path.dirname(POLICY_FILE)
        if not os.path.exists(policy_dir):
            os.makedirs(policy_dir)
            
        with open(POLICY_FILE, 'w') as f:
            json.dump(self.policies, f, indent=2)

    @defer.inlineCallbacks
    def update(self):
        if not os.path.exists(self.s_analyzer.log_path):
            return

        sessions = {}
        # Read log and group by session (efficiently if possible, but for now just read all)
        with open(self.s_analyzer.log_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    sid = event.get('session')
                    if sid:
                        if sid not in sessions:
                            sessions[sid] = []
                        sessions[sid].append(event)
                except Exception:
                    continue

        if not sessions:
            # print("DEBUG: No sessions found in log.")
            return

        # print(f"DEBUG: Found {len(sessions)} sessions in {self.s_analyzer.log_path}")

        if not hasattr(self, 'session_event_counts'):
            self.session_event_counts = {}

        updated = False
        for session_id, events in sessions.items():
            # Optimization: Skip if no new events
            if len(events) == self.session_event_counts.get(session_id, 0):
                continue
            
            try:
                self.session_event_counts[session_id] = len(events)
                summary = self.s_analyzer.summarize_session({'session_id': session_id, 'events': events})
                decision = yield self.controller.decide_level(summary)
                
                current_level = self.policies.get(session_id, {}).get('level', -1)
                current_level = self.policies.get(session_id, {}).get('level', -1)
                
                # Check for level change for concise logging
                if decision['level'] != current_level:
                    print(f"[*] Update for session {session_id}: Level {current_level} -> {decision['level']}")
                    # Force save trigger
                    self.policies[session_id] = decision
                    updated = True
                else:
                    # print(f"[*] Analysis for session {session_id}: Level remains {decision['level']}")
                    pass
                    
                # Find triggering command
                trigger_cmd = "Unknown"
                for evt in reversed(events):
                    if evt.get('eventid') == 'cowrie.command.input':
                        trigger_cmd = evt.get('input', 'Unknown')
                        break
                        
                print("\nADAPTIVE DECISION FOR session " + session_id)
                print("-" * 36)
                print(f"Trigger Command : {trigger_cmd}")
                
                # Derive detected labels
                labels = []
                rule_matches = decision['reasoning']['rule_based'].get('rule_matches', [])
                for match in rule_matches:
                    if 'wget' in match or 'curl' in match:
                        labels.append("Malware Download Attempt")
                    elif 'sudo' in match or 'su' in match:
                        labels.append("Privilege Escalation Attempt")
                    elif 'nmap' in match:
                        labels.append("Network Scanning Activity")
                    elif 'mysql' in match:
                        labels.append("Database Enumeration Attempt")
                    elif 'shadow' in match or 'passwd' in match:
                        labels.append("Credential Theft Attempt")
                    elif any(x in match for x in ['whoami', 'ifconfig', 'df', 'ls', 'pwd', 'uname']):
                        labels.append("System Discovery (Reconnaissance)")
                
                if not labels and decision['reasoning']['rule_based']['risk_score'] > 0:
                        labels.append("Suspicious Activity Detected")
        
                unique_labels = list(set(labels))
                print(f"Detected Labels : {unique_labels}")
                
                llm_summary = decision['reasoning']['llm_based'].get('summary', 'N/A')
                print(f"LLM Summary     : {llm_summary}\n")
                
                print("Policy Output:")
                policy_output = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "interaction_level": "VERY_HIGH" if decision['level'] == 3 else ("HIGH" if decision['level'] == 2 else ("MEDIUM" if decision['level'] == 1 else "LOW")),
                    "command_realism": "FULL" if decision['level'] >= 2 else "PARTIAL",
                    "filesystem_depth": "DEEP" if decision['level'] >= 2 else "SHALLOW",
                    "response_delay": 0,
                    "logging_level": "MAXIMUM",
                    "reason": decision['reasoning']['llm_based'].get('intent', 'Unknown')
                }
                print(json.dumps(policy_output, indent=4))
                print("-" * 36 + "\n")

                if decision['level'] != current_level:
                    self.policies[session_id] = decision
                    updated = True
            except Exception as e:
                print(f"[!] Error processing session {session_id}: {e}")
                import traceback
                traceback.print_exc()
        
        if updated:
            self.save_policies()

    def run(self):
        print("[*] Loop starting...")
        
        # Catch up with existing logs to avoid replaying history
        print("[*] Synchronizing with existing logs...")
        sessions = self.s_analyzer.parse_logs()
        self.session_event_counts = {}
        for session_id, events in sessions.items():
            self.session_event_counts[session_id] = len(events)
        print(f"[*] Waiting for NEW activity...")

        # Poll every 1 second for better responsiveness
        l = task.LoopingCall(self.update)
        l.start(1.0)
        reactor.run()

if __name__ == "__main__":
    live_controller = LiveAdaptiveController()
    print("[*] Starting Live Adaptive Controller...")
    live_controller.run()
