import time
import sys
import logging
import uuid

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResonanceVerify")

def verify():
    print("CORE: Testing Resonance Routing (The Flow)...")
    
    try:
        from vibe_core.mahamantra.reactor.loop import get_loop
        
        # 1. Wake the Loop (and Narada)
        loop, _ = get_loop()
        time.sleep(5.0) # Wait for spawn
        
        if not loop._bus:
             print("FAIL: Narada (EventBus) is sleeping.")
             sys.exit(1)
             
        # 2. Define Inputs
        test_key = f"resonance_test_{uuid.uuid4().hex[:4]}"
        test_val = "hare_krishna"
        
        # 3. Publish Intent: REMEMBER (Broadcast)
        # Note: We are NOT telling it "Go to Kapila". 
        # We are just yelling "REMEMBER THIS!" into the void.
        test_task_id = str(uuid.uuid4())
        
        loop.publish(
            event_type="REMEMBER",
            agent_id="tester",
            message="Please remember this",
            details={"key": test_key, "value": test_val},
            task_id=test_task_id
        )
        
        # 4. Wait for Resonance (COMPLETED event)
        # We poll the bus history.
        print("[2] Waiting for Resonance (COMPLETED)...")
        found = False
        for _ in range(10):
            time.sleep(0.5)
            history = loop._bus.get_history(limit=10, event_type="COMPLETED")
            for event in history:
                if event.agent_id == "kapila" and "Processed REMEMBER" in event.message:
                    print(f"SUCCESS: Kapila Resonated! '{event.message}'")
                    found = True
                    break
            if found:
                break
                
        if not found:
            print("FAIL: No resonance detected. Kapila did not answer.")
            sys.exit(1)
            
        # 5. Publish Intent: RECALL (Broadcast)
        print(f"[3] Broadcasting RECALL: {test_key}")
        recall_task_id = str(uuid.uuid4())
        
        loop.publish(
            event_type="RECALL",
            agent_id="tester",
            message="Recall this",
            details={"key": test_key},
            task_id=recall_task_id
        )
        # We need to pass a task_id to correlate, but publish returns event_id.
        # Ideally we pass task_id in details or modify publish.
        # But wait! Kapila.on_event looks for event.task_id.
        # Our simple publish doesn't set task_id on the Event object easily without modification?
        # Let's check loop.publish... it calls bus.emit_sync...
        # bus.emit_sync creates Event(). It doesn't accept task_id arg.
        # Ah. We might need to fix that or put it in details.
        
        # For now, let's just check if ANY recall completes for this key.
        # Kapila puts result in details={"result": ...}
        
        print("[4] Waiting for Recall Result...")
        found_recall = False
        for _ in range(10):
            time.sleep(0.5)
            history = loop._bus.get_history(limit=10, event_type="COMPLETED")
            for event in history:
                 if event.agent_id == "kapila" and "Processed RECALL" in event.message:
                     result = event.details.get("result")
                     print(f"DEBUG: Recall Result: {result}")
                     if result == test_val:
                         print(f"SUCCESS: Recalled correct value: {result}")
                         found_recall = True
                         break
            if found_recall:
                break
                
        if not found_recall:
            print("FAIL: Recall failed or incorrect value.")
            sys.exit(1)

        print("SUCCESS: Resonance Routing Verified.")
        sys.exit(0)
        
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
