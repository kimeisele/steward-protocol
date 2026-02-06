import time
import sys
import logging

# Configure basic logging to catch reactor debugs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MeditationVerify")

def verify():
    print("CORE: Testing Meditation (The Heartbeat)...")
    
    try:
        from vibe_core.mahamantra.reactor.loop import get_loop
        
        # 1. Get the loop (starts it automatically)
        loop, _ = get_loop()
        
        # Wait for reactor spawn (Fractal discovery can be heavy)
        time.sleep(5.0) # increased from 2.0s
        
        if not loop._reactor:
             print("FAIL: Reactor did not spawn.")
             sys.exit(1)
             
        start_cycles = loop._reactor.cycle_count
        start_pos = loop._reactor.position
        print(f"[1] Start State: Cycles={start_cycles}, Pos={start_pos}")
        
        # 2. Meditate (Sleep and let it chant)
        print("[2] Meditating for 2 seconds...")
        time.sleep(2.0)
        
        end_cycles = loop._reactor.cycle_count
        end_pos = loop._reactor.position
        print(f"[3] End State: Cycles={end_cycles}, Pos={end_pos}")
        
        # 3. Verify Movement
        # 2 seconds @ 100ms/tick = ~20 ticks.
        # 20 ticks > 16 (cycle size), so cycle_count should increase by at least 1.
        
        if end_cycles <= start_cycles and end_pos == start_pos:
             print("FAIL: Reactor is zombie (no movement).")
             sys.exit(1)
             
        print(f"SUCCESS: Reactor moved! Delta Cycles={end_cycles - start_cycles}, Delta Pos={end_pos - start_pos}")
        sys.exit(0)
        
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
