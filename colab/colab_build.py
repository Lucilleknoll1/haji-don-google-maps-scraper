import os
import subprocess

env = os.environ.copy()
env["PATH"] = "/usr/local/go/bin:" + env["PATH"]
env["GOTOOLCHAIN"] = "local"

build = subprocess.run(
    ["/usr/local/go/bin/go", "build", "-o", "/content/gmaps-scraper", "."],
    cwd="/content/gmaps",
    env=env,
    capture_output=True,
    text=True,
)
print("BUILD RC", build.returncode)
print(build.stdout[-3000:])
print(build.stderr[-5000:])

if build.returncode == 0:
    ver = subprocess.run(["/content/gmaps-scraper", "-version"], capture_output=True, text=True)
    print("VERSION", ver.stdout.strip(), ver.stderr.strip())
