import os
import subprocess

env = os.environ.copy()
env["PATH"] = "/usr/local/go/bin:" + env["PATH"]
env["GOTOOLCHAIN"] = "local"

r = subprocess.run(
    ["/usr/local/go/bin/go", "test", "./gmaps/...", "-count=1"],
    cwd="/content/gmaps",
    env=env,
    capture_output=True,
    text=True,
)

print("RC", r.returncode)
print("STDOUT")
print(r.stdout[-12000:])
print("STDERR")
print(r.stderr[-6000:])
