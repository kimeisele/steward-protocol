import subprocess
import sys

with open("boot.stdout.log", "w") as f_out, open("boot.stderr.log", "w") as f_err:
    process = subprocess.Popen([sys.executable, "boot.py", "--verbose"], stdout=f_out, stderr=f_err)
    process.wait()
