# rule_based_analyzer.py
# Deterministic SSH behavior classification
# Uses ONLY session analyzer output

from session_analyzer import get_session_facts


def analyze_behavior(session_facts):
    commands = session_facts["commands"]

    detected = set()

    # Reconnaissance
    recon_cmds = {"ls", "pwd", "whoami", "uname", "id", "df"}
    if any(cmd.split()[0] in recon_cmds for cmd in commands):
        detected.add("Reconnaissance")

    # Network Discovery / Scanning
    if any(cmd.split()[0] == "nmap" for cmd in commands):
        detected.add("Network Discovery / Scanning")

    # Database Service Interaction
    if any(cmd.split()[0] == "mysql" for cmd in commands):
        detected.add("Database Service Interaction")

    # Privilege escalation
    priv_cmds = {"sudo", "su"}
    if any(cmd.split()[0] in priv_cmds for cmd in commands):
        detected.add("Privilege Escalation Attempt")

    # Malware download
    malware_cmds = {"wget", "curl", "ftp", "scp"}
    if any(cmd.split()[0] in malware_cmds for cmd in commands):
        detected.add("Malware Download Attempt")

    if not detected:
        detected.add("Benign / Unknown")

    return list(detected)


if __name__ == "__main__":
    session_facts = get_session_facts()
    results = analyze_behavior(session_facts)

    print("\nRULE-BASED ANALYSIS RESULT")
    print("--------------------------")
    for r in results:
        print("-", r)

