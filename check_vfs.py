import pickle
import sys
import os

# Define constants as in Cowrie's fs.py
A_NAME, A_TYPE, A_UID, A_GID, A_SIZE, A_MODE, A_CTIME, A_CONTENTS, A_TARGET, A_REALFILE = range(10)

def list_files(fs, path="/"):
    print(f"Listing {path}:")
    if path == "/":
        curr = fs
    else:
        parts = path.strip("/").split("/")
        curr = fs
        for part in parts:
            if not part: continue
            found = False
            for item in curr[A_CONTENTS]:
                if item[A_NAME] == part:
                    curr = item
                    found = True
                    break
            if not found:
                print(f"Path {path} not found!")
                return
    
    if curr[A_TYPE] != 1: # T_DIR
        print(f"{path} is not a directory")
        return

    if not curr[A_CONTENTS]:
        print("  (empty)")
        return

    for item in curr[A_CONTENTS]:
        name = item[A_NAME]
        type_str = "DIR" if item[A_TYPE] == 1 else "FILE"
        print(f"  {type_str:4} {name}")

def main():
    pickle_path = "/home/dhikshanya06/Cowrie/src/cowrie/data/fs.pickle"
    if not os.path.exists(pickle_path):
        print(f"Pickle not found at {pickle_path}")
        return

    with open(pickle_path, "rb") as f:
        try:
            fs = pickle.load(f)
        except Exception as e:
            # Try with encoding if it fails
            f.seek(0)
            try:
                fs = pickle.load(f, encoding="utf8")
            except Exception as e2:
                print(f"Failed to load pickle: {e2}")
                return

    list_files(fs, "/usr/local/bin")
    list_files(fs, "/var/log")
    list_files(fs, "/var/www")
    list_files(fs, "/opt")
    list_files(fs, "/media")
    list_files(fs, "/mnt")

if __name__ == "__main__":
    main()
