import json
import os
import re
import subprocess
import time

BIN = "/content/gmaps-scraper"
QUERIES = "/content/bench_queries.txt"
GEO = "40.9312,-73.8988"

with open(QUERIES, "w", encoding="utf-8") as f:
    f.write("\n".join([
        "coffee shops in Yonkers NY",
        "restaurants in Yonkers NY",
        "gyms in Yonkers NY",
    ]) + "\n")


def run(concurrency):
    out = f"/content/bench_c{concurrency}.json"
    log = f"/content/bench_c{concurrency}.log"
    if os.path.exists(out):
        os.remove(out)

    cmd = [
        BIN,
        "-input", QUERIES,
        "-geo", GEO,
        "-zoom", "15",
        "-lang", "en",
        "-depth", "1",
        "-c", str(concurrency),
        "-json",
        "-results", out,
        "-exit-on-inactivity", "2m",
    ]

    started = time.time()
    with open(log, "w", encoding="utf-8") as log_file:
        proc = subprocess.run(cmd, cwd="/content", stdout=log_file, stderr=subprocess.STDOUT, timeout=600)
    elapsed = time.time() - started

    count = 0
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            count = sum(1 for line in f if line.strip())

    text = open(log, encoding="utf-8", errors="replace").read()
    errors = text.count('"level":"error"')
    failed = [int(x) for x in re.findall(r'"numOfJobsFailed":(\d+)', text)]
    completed = [int(x) for x in re.findall(r'"numOfJobsCompleted":(\d+)', text)]

    return {
        "concurrency": concurrency,
        "seconds": round(elapsed, 1),
        "entries": count,
        "errors": errors,
        "max_jobs_failed": max(failed) if failed else 0,
        "max_jobs_completed": max(completed) if completed else 0,
    }


first = run(2)
print("RESULT_C2", json.dumps(first), flush=True)
time.sleep(45)
second = run(3)
print("RESULT_C3", json.dumps(second), flush=True)

if first["seconds"] and second["seconds"]:
    print("SPEEDUP_C3_VS_C2", round(first["seconds"] / second["seconds"], 2), flush=True)
