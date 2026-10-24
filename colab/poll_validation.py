import glob
import os

for path in ["/content/val_runner.log"] + sorted(glob.glob("/content/val_*.log")):
    if os.path.exists(path):
        print("LOG", path, os.path.getsize(path))
        with open(path, errors="replace") as f:
            print(f.read()[-700:])

print("DONE_MARKER", os.path.exists("/content/val_done"))
for path in sorted(glob.glob("/content/val_*.json")):
    print("OUT", path, os.path.getsize(path))
