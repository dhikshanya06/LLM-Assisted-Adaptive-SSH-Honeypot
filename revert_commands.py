import os

COMMANDS_DIR = "src/cowrie/commands"

def revert_command_file(filepath):
    if not filepath.endswith(".py") or filepath.endswith("__init__.py"):
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    new_lines = []
    updated = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match the injected check
        if "if self.interaction_level == 0:" in line and i + 1 < len(lines) and "return" in lines[i+1]:
            # Skip these two lines
            i += 2
            updated = True
            continue
        new_lines.append(line)
        i += 1

    if updated:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"Reverted {filepath}")

if __name__ == "__main__":
    for filename in os.listdir(COMMANDS_DIR):
        revert_command_file(os.path.join(COMMANDS_DIR, filename))
    # Also revert bash.py specifically if it was missed or handled differently
    revert_command_file("src/cowrie/commands/bash.py")
