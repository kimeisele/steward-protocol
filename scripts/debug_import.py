print("Step 1: Start", flush=True)

try:
    print("Importing Task...", flush=True)

    print("Importing Errors...", flush=True)

    print("Importing Scheduler...", flush=True)

    print("Importing Kernel...", flush=True)
    from vibe_core.kernel_impl import RealVibeKernel

    print("Step 2: Import Successful", flush=True)
except Exception as e:
    print(f"Step 2: Import Failed: {e}", flush=True)

try:
    print("Initializing Kernel (safe mode)...", flush=True)
    k = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
    print("Step 3: Init Successful", flush=True)
except Exception as e:
    print(f"Step 3: Init Failed: {e}", flush=True)

try:
    print("Booting Kernel...", flush=True)
    k.boot()
    print("Step 4: Boot Successful", flush=True)
except Exception as e:
    print(f"Step 4: Boot Failed: {e}", flush=True)
