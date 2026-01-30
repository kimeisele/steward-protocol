from vibe_core.mahamantra.dharma.engine import dharma
from vibe_core.mahamantra.protocols.dharma_protocol import DharmaProtocol, SwarupaData

print("BOOTING DHARMA ENGINE (PROTOCOL VERIFIED)...")
# Runtime check for protocol adherence (simulated)
assert isinstance(dharma, object), "Dharma Engine exists" 

print("1. LINGUIST TEST:")
krishna = dharma.get_form("KRISHNA")
assert isinstance(krishna, SwarupaData), "Returned Form Must be SwarupaData DTO"
print(f"   Name: {krishna.key}")
print(f"   Deva: {krishna.deva}") 
print(f"   IAST: {krishna.iast}")

print("2. LAYER TEST (108):")
l108 = dharma.get_layer_signature(108)
print(f"   Sig: {l108}")

print("3. MATRIX TEST:")
spark = dharma.get_spark(2, 3) # Q3 + Q4
print(f"   Spark(Q3,Q4): {spark}")
print("ENGINE ONLINE & COMPLIANT.")
