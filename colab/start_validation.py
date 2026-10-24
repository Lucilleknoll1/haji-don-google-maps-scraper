import subprocess

p = subprocess.Popen(
    ["bash", "/content/run_validation.sh"],
    start_new_session=True,
    stdout=open("/content/val_runner.log", "w"),
    stderr=subprocess.STDOUT,
)
print("PID", p.pid)
