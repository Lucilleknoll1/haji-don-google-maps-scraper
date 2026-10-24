import subprocess

r = subprocess.run(
    ["python3", "/content/outreach_leads.py", "/content/out.json", "/content/leads.csv"],
    capture_output=True,
    text=True,
)
print("RC", r.returncode)
print(r.stdout)
print(r.stderr)
