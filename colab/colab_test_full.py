import os
import subprocess

if not os.path.isdir("/content/gmaps"):
    subprocess.run(
        ["git", "clone", "--depth", "1",
         "https://github.com/Lucilleknoll1/haji-don-google-maps-scraper.git", "/content/gmaps"],
        check=True,
    )

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
print(r.stdout[-5000:])
print(r.stderr[-3000:])
