import os
import subprocess

env = os.environ.copy()
env["PATH"] = "/usr/local/go/bin:" + env["PATH"]
env["GOTOOLCHAIN"] = "local"

r = subprocess.run(
    ["/usr/local/go/bin/go", "run", "./tools/verifyui", "/content/verify_sample.csv", "/content/verify_results.csv"],
    cwd="/content/gmaps",
    env=env,
    capture_output=True,
    text=True,
    timeout=600,
)
print("RC", r.returncode)
print(r.stdout[-3000:])
print(r.stderr[-3000:])
