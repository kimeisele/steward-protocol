import time
import sys
import logging
import uuid
import threading

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("DojoVerify")

def verify():
    print("CORE: Testing Legacy Dojo Mounting (Meditation)...")
    
    try:
        from vibe_core.mahamantra.reactor.loop import get_loop, ReactorLoop
        
        # 1. Wake the Loop
        # get_loop() starts the thread if not started
        loop, _ = get_loop()
        
        print("[1] ReactorLoop started. Waiting for meditation...")
        time.sleep(5.0) 
        
        if not loop._dojo:
             print("FAIL: DojoRunner is NOT initialized in loop.")
             sys.exit(1)
             
        # Check if dojo initialized internal state
        if not loop._dojo._meditation_initialized:
            # Maybe it hasn't ticked enough yet?
            print("WARN: Dojo meditation state not yet initialized. Waiting more...")
            time.sleep(5.0)
            
        if not loop._dojo._meditation_initialized:
             print("FAIL: Dojo meditation did not initialize.")
             sys.exit(1)
             
        print("[2] Dojo initialized. Checking for activity...")
        
        # We can't easily capture logs from here without a custom handler,
        # but we can check if the queue is being consumed.
        initial_queue_len = len(loop._dojo._meditation_queue)
        print(f"DEBUG: Initial Queue Len: {initial_queue_len}")
        
        time.sleep(2.0)
        
        current_queue_len = len(loop._dojo._meditation_queue)
        print(f"DEBUG: Current Queue Len: {current_queue_len}")
        
        if current_queue_len < initial_queue_len:
            print(f"SUCCESS: Queue consumed! ({initial_queue_len} -> {current_queue_len})")
            print("Legacy Dojo is Alive and Meditating.")
        elif current_queue_len == 0 and initial_queue_len == 0:
            print("FAIL: Queue empty? Should have loaded mixed scenarios.")
            sys.exit(1)
        else:
            print(f"FAIL: Queue did not move. Is meditate_tick being called? ticks={loop._idle_ticks}")
            
            # Force tick?
            # loop._dojo.meditate_tick()
            sys.exit(1)

        sys.exit(0)
        
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        # traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify()
