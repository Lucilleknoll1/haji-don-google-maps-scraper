import os
import subprocess

subprocess.run(["unzip", "-o", "/content/gmaps_patch.zip", "-d", "/content/gmaps"], check=True)

env = os.environ.copy()
env["PATH"] = "/usr/local/go/bin:" + env["PATH"]
env["GOTOOLCHAIN"] = "local"

pattern = "^(Test_EntryFromJSON|Test_EntryFromJSONStatusFallback|TestBusinessFlagsUnclaimedFixture|TestBusinessFlagsClaimedFixture|TestBusinessStatusClassification|TestClaimStateFromFlags)$"

r = subprocess.run(
    ["/usr/local/go/bin/go", "test", "./gmaps/...", "-run", pattern, "-count=1", "-v"],
    cwd="/content/gmaps",
    env=env,
    capture_output=True,
    text=True,
)

print("RC", r.returncode)
for line in (r.stdout + "\n" + r.stderr).splitlines():
    if any(k in line for k in ("FAIL", "PASS", "Error Trace", "Error:", "expected", "actual", "cannot", "undefined", "mismatch")):
        print(line)
