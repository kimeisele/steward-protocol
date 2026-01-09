"""
DWARAPALA PROTOCOL - The Gatekeepers (Jaya & Vijaya).
=====================================================
"Service has no Will. Only Person has Will."

This module strictly separates 'Service' (Mechanism) from 'Person' (Authority).
It replaces loose 'Context' checks with strict 'PersonProtocol' checks.
"""

from typing import TypeVar, Generic, Optional, TYPE_CHECKING
from vibe_core.protocols.types import PersonProtocol, Capability, ServiceProtocol

# Defer/Safe Import for The37th to avoid any weirdness, though protocols usually compile fine.
# But verify_accessor is runtime. 
# We need to import The37th at top level or inside if circular.
# Let's try top level first.
from vibe_core.protocols.universal.the_37th import The37th

# Generic for the Resource being accessed
T_Resource = TypeVar("T_Resource")

class AccessDenied(Exception):
    """Blocked by Jaya/Vijaya."""
    pass

class DwarapalaGate:
    """
    The Gatekeeper.
    Enforces: Only Persons can execute Verbs.
    """
    
    @staticmethod
    def verify_accessor(accessor: object, required_capability: str) -> PersonProtocol:
        """
        The Check.
        1. Is 'accessor' a Person? (Not just a Service)
        2. Does 'Person' have the Capability?
        
        *SPECIAL*: Checks for 'The37th' (Divine Override).
        """
        
        # 0. THE 37TH PRINCIPLE (Venu-Gita Override)
        # If the accessor is the Supreme Person revealing Himself,
        # The Gatekeepers are stunned/sleeping in bliss.
        if isinstance(accessor, The37th):
            if accessor.reveal():
                # ACCESS GRANTED (Override)
                return accessor # type: ignore (The37th is a PersonProtocol)
        
        # 1. ONTOLOGICAL CHECK: Is it a Person?
        if not isinstance(accessor, PersonProtocol):
            # It is a Service or a Thing. Block it.
            # Services must work *on behalf* of a Person, they cannot BE the accessor.
            raise AccessDenied(
                f"Identity Crisis: {type(accessor).__name__} is a Service/Object, not a Person. "
                "Services cannot wield Capabilities."
            )
            
        # 2. CAPABILITY CHECK: Does the Person have the Right?
        # We search the set of capabilities strictly.
        has_cap = False
        for cap in accessor.capabilities:
            if cap.name == required_capability:
                has_cap = True
                break
                
        if not has_cap:
            raise AccessDenied(
                f"Adhikara Failure: Person '{accessor.name}' lacks capability '{required_capability}'."
            )
            
        return accessor

    @staticmethod
    def open_gate(person: PersonProtocol, resource: T_Resource) -> T_Resource:
        """
        Allows the Person to access the Resource.
        Returns the resource (Pass-through) if allowed.
        """
        # (Jaya & Vijaya bow)
        return resource
