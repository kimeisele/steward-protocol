import subprocess


def run(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"CMD: {cmd}")
        print(f"RTN: {res.returncode}")
        print(f"OUT:\n{res.stdout}")
        print(f"ERR:\n{res.stderr}")
    except Exception as e:
        print(f"EXEC ERROR: {e}")


run("git status")
run("git branch -vv")
run("git log -1 origin/feature/opus-005-unification")
