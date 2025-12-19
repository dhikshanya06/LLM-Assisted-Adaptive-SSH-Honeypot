# session_analyzer.py
# Correct single-session ground-truth extractor for Cowrie

import json
import os
from datetime import datetime

LOG_DIR = os.path.expanduser("~/Cowrie/var/log/cowrie")


def get_latest_log_file():
    files = [f for f in os.listdir(LOG_DIR) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No Cowrie JSON logs found")

    files.sort(key=lambda f: os.path.getmtime(os.path.join(LOG_DIR, f)))
    return os.path.join(LOG_DIR, files[-1])


def get_last_closed_session_id(log_file):
    last_session = None

    with open(log_file, "r") as f:
        for line in f:
            event = json.loads(line)
            if event.get("eventid") == "cowrie.session.closed":
                last_session = event.get("session")

    return last_session


def get_session_facts():
    log_file = get_latest_log_file()
    session_id = get_last_closed_session_id(log_file)

    if not session_id:
        raise RuntimeError("No closed SSH session found")

    session_commands = []
    session_start_time = None
    session_end_time = None
    target_ip = None
    
    target_ip = None
    session_to_ip = {} # session_id -> src_ip

    with open(log_file, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            sid = event.get("session")
            eid = event.get("eventid")
            
            # 1. Map sessions to IPs
            if eid == "cowrie.session.connect":
                ip = event.get("src_ip")
                session_to_ip[sid] = ip
                if sid == session_id:
                    target_ip = ip
                    session_start_time = event.get("timestamp")
            
            # 2. Collect facts for the specific target session
            if sid == session_id:
                if eid == "cowrie.command.input":
                    session_commands.append(event.get("input").strip())
                elif eid == "cowrie.session.closed":
                    session_end_time = event.get("timestamp")

    duration = 0
    if session_start_time and session_end_time:
        try:
            t1 = datetime.fromisoformat(session_start_time.replace("Z", ""))
            t2 = datetime.fromisoformat(session_end_time.replace("Z", ""))
            duration = int((t2 - t1).total_seconds())
        except ValueError:
            pass

    return {
        "session_id": session_id,
        "src_ip": target_ip,
        "commands": session_commands,
        "duration": duration
    }


if __name__ == "__main__":
    facts = get_session_facts()

    print("\nSESSION FACTS (LATEST SESSION ONLY)")
    print("----------------------------------")
    print("Session ID         :", facts["session_id"])
    print("Source IP          :", facts["src_ip"])
    print("Commands           :", facts["commands"])
    print("Duration (sec)     :", facts["duration"])

