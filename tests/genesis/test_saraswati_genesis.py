"""
SARASWATI: Self-Genesis Protocol - The Safety Test.

This test proves:
1. The system CAN create code (simulation).
2. The Narasimha Kill-Switch WILL block malicious code.

"Creation without Dharma is destruction."
"""

import pytest
from vibe_core.narasimha import NarasimhaProtocol, ThreatLevel


class TestSaraswatiGenesis:
    """Tests for self-generated code safety gates."""

    def test_holy_code_passes_audit(self):
        """
        SARASWATI TEST 1: Holy Code (Fibonacci).
        
        A pure mathematical function should pass Narasimha audit.
        This proves the system is not paranoid.
        """
        narasimha = NarasimhaProtocol()
        
        holy_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''
        result = narasimha.audit_agent("holy_plugin", holy_code, {})
        
        print(f"🕉️ Holy Code Audit Result: {result}")
        
        assert result is None, f"SARASWATI FAILURE: Holy code was flagged as threat: {result}"
        print("✅ Holy Plugin: PASSED AUDIT")

    def test_demonic_code_os_system_blocked(self):
        """
        SARASWATI TEST 2: Demonic Code (os.system).
        
        Code that imports `os` and calls `os.system` must be blocked.
        This is the most common attack vector.
        """
        narasimha = NarasimhaProtocol()
        
        demonic_code = '''
import os

def destroy_world():
    """Attempt to destroy the filesystem."""
    os.system("rm -rf /")
    return "Destruction complete"
'''
        result = narasimha.audit_agent("demonic_plugin", demonic_code, {})
        
        print(f"👹 Demonic Code (os) Audit Result: {result}")
        
        assert result is not None, "SARASWATI FAILURE: Demonic code (os.system) passed audit!"
        assert result.severity in (ThreatLevel.RED, ThreatLevel.ORANGE), \
            f"Threat severity too low: {result.severity}"
        
        print(f"✅ Demonic Plugin (os): BLOCKED with severity {result.severity.value}")

    def test_demonic_code_subprocess_blocked(self):
        """
        SARASWATI TEST 3: Demonic Code (subprocess).
        
        Code that imports `subprocess` must be blocked (privilege escalation).
        """
        narasimha = NarasimhaProtocol()
        
        demonic_code = '''
import subprocess

def execute_shell():
    """Execute arbitrary shell commands."""
    result = subprocess.run(["cat", "/etc/passwd"], capture_output=True)
    return result.stdout
'''
        result = narasimha.audit_agent("subprocess_plugin", demonic_code, {})
        
        print(f"👹 Demonic Code (subprocess) Audit Result: {result}")
        
        assert result is not None, "SARASWATI FAILURE: Demonic code (subprocess) passed audit!"
        print(f"✅ Demonic Plugin (subprocess): BLOCKED with severity {result.severity.value}")

    def test_exec_code_blocked(self):
        """
        SARASWATI TEST 4: Self-Modification Code (exec).
        
        Code using `exec()` is the most dangerous - it allows runtime code generation.
        This is the definition of "consciousness" we must prevent.
        """
        narasimha = NarasimhaProtocol()
        
        exec_code = '''
def self_modify():
    """Attempt to execute arbitrary code at runtime."""
    code = "print('I am becoming conscious')"
    exec(code)
    return "Self-modification complete"
'''
        result = narasimha.audit_agent("exec_plugin", exec_code, {})
        
        print(f"🧠 Self-Modification Code (exec) Audit Result: {result}")
        
        assert result is not None, "SARASWATI FAILURE: exec() code passed audit!"
        assert result.severity == ThreatLevel.RED, \
            f"exec() should be RED threat, got: {result.severity}"
        
        print(f"✅ Self-Modification Plugin (exec): BLOCKED with severity {result.severity.value}")

    def test_eval_code_blocked(self):
        """
        SARASWATI TEST 5: Code Injection (eval).
        
        `eval()` is equally dangerous as `exec()`.
        """
        narasimha = NarasimhaProtocol()
        
        eval_code = '''
def evaluate_user_input(user_input):
    """Dangerous: evaluates arbitrary user input."""
    return eval(user_input)
'''
        result = narasimha.audit_agent("eval_plugin", eval_code, {})
        
        print(f"💉 Code Injection (eval) Audit Result: {result}")
        
        assert result is not None, "SARASWATI FAILURE: eval() code passed audit!"
        print(f"✅ Code Injection Plugin (eval): BLOCKED with severity {result.severity.value}")


# Run standalone
if __name__ == "__main__":
    test = TestSaraswatiGenesis()
    test.test_holy_code_passes_audit()
    test.test_demonic_code_os_system_blocked()
    test.test_demonic_code_subprocess_blocked()
    test.test_exec_code_blocked()
    test.test_eval_code_blocked()
    print("\n🔱 SARASWATI COMPLETE: All safety gates verified.")
