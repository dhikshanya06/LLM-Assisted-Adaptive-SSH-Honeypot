# llm_analyzer.py
from session_analyzer import get_session_facts
from rule_based_analyzer import analyze_behavior

def llm_analyze(session, rule_labels):
    """
    Simulates LLM intelligence extraction by mapping rule-based labels
    to broader categories (intent, skill, attack stage).
    """
    intent = "Benign / Unknown"
    skill = "Unknown"
    stage = "Unknown"

    if "Reconnaissance" in rule_labels:
        intent = "Reconnaissance"
        stage = "Discovery"
        skill = "Low to Medium"

    if "Network Discovery / Scanning" in rule_labels:
        intent = "Network Mapping"
        stage = "Discovery"
        skill = "Medium"

    if "Database Service Interaction" in rule_labels:
        intent = "Data Exploration"
        stage = "Collection / Exfiltration"
        skill = "Medium to High"

    if "Privilege Escalation Attempt" in rule_labels:
        intent = "Privilege Escalation"
        stage = "Privilege Escalation"
        skill = "Medium"

    if "Malware Download Attempt" in rule_labels:
        intent = "Resource Development"
        stage = "Malware Installation"
        skill = "Low to Medium"

    # If multiple labels exist, pick the most "significant" one for the summary
    if len(rule_labels) > 0:
        main_label = rule_labels[0]
        summary = f"Attacker intent appears to be {intent} during the {stage} phase (based on: {', '.join(rule_labels)})."
    else:
        summary = "No suspicious behavior detected."

    return {
        "intent": intent,
        "skill_level": skill,
        "attack_stage": stage,
        "summary": summary
    }


if __name__ == "__main__":
    try:
        session_facts = get_session_facts()
        rule_output = analyze_behavior(session_facts)
        
        result = llm_analyze(session_facts, rule_output)
        
        print("\nLLM INTELLIGENCE OUTPUT")
        print("-----------------------")
        for k, v in result.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"Error during analysis: {e}")
