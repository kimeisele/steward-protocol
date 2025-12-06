import sys

from vibe_core.kernel_impl import RealVibeKernel

print(f"Kernel module: {RealVibeKernel.__module__}")
print(f"Kernel file: {sys.modules['vibe_core.kernel_impl'].__file__}")
kernel = RealVibeKernel(ledger_path=":memory:")
print(f"Has grant_capability: {hasattr(kernel, 'grant_capability')}")

try:
    kernel.grant_capability
    print("grant_capability exists and is accessible")
except AttributeError:
    print("grant_capability does NOT exist")
