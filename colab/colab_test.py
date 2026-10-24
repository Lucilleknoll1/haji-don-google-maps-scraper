import os
import shutil
import subprocess
import sys
import urllib.request

REPO = "/content/gmaps"
GO_VERSION = "1.27.3"
GO_TAR = f"go{GO_VERSION}.linux-amd64.tar.gz"
GO_URL = f"https://go.dev/dl/{GO_TAR}"


def run(cmd, cwd=None, env=None):
    print(f"\n$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def ensure_go():
    if shutil.which("go"):
        return shutil.which("go")

    if not os.path.exists("/usr/local/go/bin/go"):
        print(f"downloading {GO_URL}", flush=True)
        urllib.request.urlretrieve(GO_URL, f"/tmp/{GO_TAR}")
        shutil.rmtree("/usr/local/go", ignore_errors=True)
        run(["tar", "-C", "/usr/local", "-xzf", f"/tmp/{GO_TAR}"])

    return "/usr/local/go/bin/go"


def main():
    print("python", sys.version, flush=True)

    if not os.path.isdir(REPO):
        run(["git", "clone", "--depth", "1",
             "https://github.com/gosom/google-maps-scraper.git", REPO])

    run(["unzip", "-o", "/content/gmaps_patch.zip", "-d", REPO])

    go = ensure_go()
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(go) + os.pathsep + env["PATH"]
    env["GOTOOLCHAIN"] = "local"

    run([go, "version"], env=env)
    run([go, "fmt", "./gmaps/..."], cwd=REPO, env=env)
    run([go, "test", "./gmaps/...", "-count=1", "-v"], cwd=REPO, env=env)


if __name__ == "__main__":
    main()
