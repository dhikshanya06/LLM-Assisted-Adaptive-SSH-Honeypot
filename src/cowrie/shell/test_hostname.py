import sys
import os

# Setup path
sys.path.append("/home/dhikshanya06/cowrie/src")

from cowrie.shell.server import CowrieServer

print("[*] Testing hostname randomization...")
hostnames = set()

for i in range(10):
    try:
        # Pass None as realm since it's not used in __init__ logic we care about
        server = CowrieServer(None) 
        # Trigger fs init
        server.initFileSystem("/root")
        
        # DEBUG: Check if getfile returns anything
        hf = server.fs.getfile("/etc/hostname")
        print(f"    getfile('/etc/hostname') result type: {type(hf)}")
        if hf:
             print(f"    Current content in object: {hf[7]}") # 7 is A_CONTENTS
        else:
             print("    [!] getfile returned None!")

        print(f"[{i+1}] Hostname: {server.hostname}")
        
        # Verify FS content
        fs_hostname = server.fs.file_contents("/etc/hostname").decode().strip()
        print(f"    FS /etc/hostname: {fs_hostname}")
        
        if fs_hostname != server.hostname:
            print(f"    [!] MISMATCH: {fs_hostname} != {server.hostname}")
        
        hostnames.add(server.hostname)
    except Exception as e:
        print(f"[!] Error: {e}")

print("\nResults:")
print(f"Unique hostnames found: {len(hostnames)}")
if len(hostnames) > 1:
    print("[*] SUCCESS: Hostname is changing.")
else:
    print("[!] FAILURE: Hostname is static.")
