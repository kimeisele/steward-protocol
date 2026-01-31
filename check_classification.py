"""
CHECK CLASSIFICATION ADAPTER
=============================

Verifies the integrity of the MahaClassifier adapter.
"""

from vibe_core.mahamantra.adapters.classification import MahaClassifier, __genesis__, __mahajana__
from vibe_core.mahamantra.substrate.classifier import StructuralAlignment, ComplexitySource, MemoryModel, Determinism

def check_genesis():
    print(f"\n[CHECK] Genesis Byte: {__genesis__}")
    print(f"[CHECK] Mahajana: {__mahajana__}")
    
    # Simple check (not the full 37 check, just presence)
    assert __genesis__.startswith("0x"), "Genesis byte must be hex"
    print("[PASS] Genesis headers present.")

def check_classification_logic():
    classifier = MahaClassifier()
    
    # Test 1: Lotus Array (Perfect)
    result = classifier.classify(
        name="LotusArray",
        alignment="perfect",
        complexity="structure",
        memory="bounded_static",
        determinism="always",
        key_space_size=65536,
        max_memory_bytes=512000
    )
    
    print(f"\n[TEST 1] LotusArray Result: {result.verdict}")
    print(f"         Score: {result.mercy_advantage}")
    
    assert result.is_anukulya, "LotusArray must be ANUKULYA"
    assert result.mercy_advantage > 10, "LotusArray should have high mercy advantage"
    
    # Test 2: Neural Net (Chaotic)
    result_nn = classifier.classify(
        name="AttentionMatrix",
        alignment="none",
        complexity="quadratic",
        memory="unbounded_gc",
        determinism="chaotic",
        key_space_size=100000,
        max_memory_bytes=-1
    )
    
    print(f"\n[TEST 2] NeuralNet Result: {result_nn.verdict}")
    
    assert not result_nn.is_anukulya, "NeuralNet shoud be PRATIKULYA (or low score)"
    
    print("[PASS] Logic verification successful.")

if __name__ == "__main__":
    check_genesis()
    check_classification_logic()
