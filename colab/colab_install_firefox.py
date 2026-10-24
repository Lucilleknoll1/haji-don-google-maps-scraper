import os
import subprocess

env = os.environ.copy()
env["PATH"] = "/usr/local/go/bin:" + env["PATH"]
env["GOTOOLCHAIN"] = "local"

cmd = [
    "/usr/local/go/bin/go", "run",
    "github.com/mxschmitt/playwright-go/cmd/playwright@v0.6100.0",
    "install", "firefox", "--with-deps",
]

r = subprocess.run(cmd, cwd="/content/gmaps", env=env, capture_output=True, text=True)
print("RC", r.returncode)
print(r.stdout[-4000:])
print(r.stderr[-4000:])
