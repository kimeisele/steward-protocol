"""
NARADA SCANNER - Auto-Discovery für NAGA Services.

"Narada unterrichtete Prahlad im Mutterleib - er injizierte den göttlichen
Code in die Dämonen-Infrastruktur, BEVOR die Runtime überhaupt startete."
(SB 7.7.15)

This is the Dependency Injection mechanism that:
1. Scans vibe_core/naga/services/*.py at boot
2. Finds all @naga_service decorated classes
3. Validates them against Kulika (Schema Registry)
4. Registers them in ServiceRegistry + CorrectionHandler

This REPLACES manual ServiceRegistry.register() calls in orchestrator.py.

Usage:
    from vibe_core.naga.scanner import NaradaScanner

    scanner = NaradaScanner()
    discovered = scanner.scan()
    scanner.register_all(correction_orchestrator)
"""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Type

from vibe_core.di import ServiceRegistry
from vibe_core.naga.kulika import (
    KulikaRegistry,
    NagaDomain,
    NagaLord,
    NagaManifest,
    get_kulika,
)

if TYPE_CHECKING:
    from vibe_core.correction import CorrectionOrchestrator

logger = logging.getLogger("NAGA.NARADA.SCANNER")


class NaradaScanner:
    """
    Narada - The Auto-Discovery Scanner.

    Scans for @naga_service decorated classes and registers them.
    Replaces manual ServiceRegistry.register() calls.

    Philosophy:
        "A living system grows organically.
         It is not defined in a static list."
    """

    # Default locations to scan
    DEFAULT_SCAN_PATHS = [
        "vibe_core.naga.services",
    ]

    def __init__(
        self,
        scan_paths: Optional[List[str]] = None,
        kulika: Optional[KulikaRegistry] = None,
    ):
        """
        Initialize the scanner.

        Args:
            scan_paths: Module paths to scan (default: vibe_core.naga.services)
            kulika: KulikaRegistry instance (default: singleton)
        """
        self._scan_paths = scan_paths or self.DEFAULT_SCAN_PATHS
        self._kulika = kulika or get_kulika()
        self._discovered: Dict[str, Tuple[Type, NagaManifest]] = {}
        self._instances: Dict[str, Any] = {}
        self._scanned = False

    def scan(self) -> List[NagaManifest]:
        """
        Scan for @naga_service decorated classes.

        Returns:
            List of discovered NagaManifest objects
        """
        self._discovered.clear()

        for module_path in self._scan_paths:
            self._scan_module(module_path)

        self._scanned = True
        logger.info(f"Narada discovered {len(self._discovered)} NAGA services")

        return [manifest for _, manifest in self._discovered.values()]

    def _scan_module(self, module_path: str) -> None:
        """Scan a module path for NAGA services."""
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.warning(f"Cannot import {module_path}: {e}")
            return

        # Get the module's directory for submodule scanning
        if hasattr(module, "__path__"):
            # It's a package, scan submodules
            for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
                full_name = f"{module_path}.{modname}"
                self._scan_single_module(full_name)
        else:
            # It's a single module
            self._scan_single_module(module_path)

    def _scan_single_module(self, module_path: str) -> None:
        """Scan a single module for NAGA services."""
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.debug(f"Cannot import {module_path}: {e}")
            return

        # Find all classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip if not defined in this module
            if obj.__module__ != module_path:
                continue

            # Check for _naga_manifest attribute (set by @naga_service)
            if hasattr(obj, "_naga_manifest"):
                manifest: NagaManifest = obj._naga_manifest
                key = manifest.name.lower()

                # Validate
                errors = self._kulika.validate(obj)
                if errors:
                    logger.warning(f"NAGA {manifest.name} validation failed: {errors}")
                    continue

                self._discovered[key] = (obj, manifest)
                logger.debug(f"Discovered NAGA: {manifest.name} ({manifest.lord.value})")

    def register_all(
        self,
        correction_orchestrator: Optional["CorrectionOrchestrator"] = None,
        create_instances: bool = False,
        instance_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> int:
        """
        Register all discovered NAGAs in Kulika and ServiceRegistry.

        Args:
            correction_orchestrator: For registering CorrectionHandlers
            create_instances: Whether to create instances (default: False)
            instance_kwargs: Constructor kwargs per service name

        Returns:
            Number of services registered
        """
        if not self._scanned:
            self.scan()

        instance_kwargs = instance_kwargs or {}
        registered = 0

        for name, (cls, manifest) in self._discovered.items():
            # Register in Kulika
            self._kulika.register(cls)

            # Create instance if requested
            instance = None
            if create_instances:
                kwargs = instance_kwargs.get(name, {})
                try:
                    instance = cls(**kwargs)
                    self._instances[name] = instance
                    self._kulika.set_instance(name, instance)
                except Exception as e:
                    logger.error(f"Failed to create {manifest.name}: {e}")
                    continue

            # Register in ServiceRegistry if we have a protocol class
            if manifest.protocol_class and instance:
                try:
                    # Dynamically import the protocol
                    parts = manifest.protocol_class.rsplit(".", 1)
                    if len(parts) == 2:
                        proto_module = importlib.import_module(parts[0])
                        proto_class = getattr(proto_module, parts[1])
                        ServiceRegistry.register(proto_class, instance)
                        logger.debug(f"Registered {manifest.name} in ServiceRegistry")
                except Exception as e:
                    logger.warning(f"Failed to register {manifest.name} protocol: {e}")

            # Register CorrectionHandler if drift_source specified
            if manifest.drift_source and correction_orchestrator and instance:
                if hasattr(instance, "as_handler"):
                    try:
                        from vibe_core.protocols.correction import DriftSource

                        drift_source = DriftSource(manifest.drift_source)
                        correction_orchestrator.dispatcher.register_handler(
                            drift_source,
                            instance.as_handler(),
                            handler_id=name,
                            priority=manifest.priority,
                        )
                        logger.debug(f"Registered {manifest.name} CorrectionHandler for {manifest.drift_source}")
                    except Exception as e:
                        logger.warning(f"Failed to register {manifest.name} handler: {e}")

            registered += 1

        logger.info(f"Narada registered {registered} NAGA services")
        return registered

    def get_instance(self, name: str) -> Optional[Any]:
        """Get a created instance by name."""
        return self._instances.get(name.lower())

    def set_instance(self, name: str, instance: Any) -> None:
        """Set an instance (for external creation)."""
        name = name.lower()
        self._instances[name] = instance
        self._kulika.set_instance(name, instance)

    def get_discovered(self) -> Dict[str, NagaManifest]:
        """Get all discovered manifests."""
        return {name: manifest for name, (_, manifest) in self._discovered.items()}

    def get_class(self, name: str) -> Optional[Type]:
        """Get a discovered class by name."""
        entry = self._discovered.get(name.lower())
        return entry[0] if entry else None

    def generate_report(self) -> str:
        """
        Generate a markdown report of discovered NAGAs.

        This can be used by ManifestationService to generate NAGASERVICE.md.
        """
        if not self._scanned:
            self.scan()

        lines = [
            "# NAGA Service Agency - Live Status",
            "",
            f"> Auto-generated by Narada Scanner. {len(self._discovered)} services discovered.",
            "",
            "## Infrastructure Layer (Real Nagas)",
            "",
            "| Lord | Name | DriftSource | Priority | Capabilities |",
            "|------|------|-------------|----------|--------------|",
        ]

        # Infrastructure
        infra = [(name, m) for name, (_, m) in self._discovered.items() if m.domain == NagaDomain.INFRASTRUCTURE]
        for name, manifest in sorted(infra, key=lambda x: x[1].priority, reverse=True):
            caps = ", ".join(c.value for c in manifest.capabilities) or "-"
            drift = manifest.drift_source or "-"
            lines.append(f"| {manifest.lord.value} | {manifest.name} | {drift} | {manifest.priority} | {caps} |")

        lines.extend(
            [
                "",
                "## Governance Layer (Personnel)",
                "",
                "| Lord | Name | DriftSource | Priority | Capabilities |",
                "|------|------|-------------|----------|--------------|",
            ]
        )

        # Governance
        gov = [(name, m) for name, (_, m) in self._discovered.items() if m.domain == NagaDomain.GOVERNANCE]
        for name, manifest in sorted(gov, key=lambda x: x[1].priority, reverse=True):
            caps = ", ".join(c.value for c in manifest.capabilities) or "-"
            drift = manifest.drift_source or "-"
            lines.append(f"| {manifest.lord.value} | {manifest.name} | {drift} | {manifest.priority} | {caps} |")

        lines.extend(
            [
                "",
                "## DriftSource Coverage",
                "",
                "| DriftSource | Handler | Priority |",
                "|-------------|---------|----------|",
            ]
        )

        # DriftSource coverage
        drift_handlers = {}
        for name, (_, manifest) in self._discovered.items():
            if manifest.drift_source:
                drift_handlers[manifest.drift_source] = (manifest.name, manifest.priority)

        for drift, (handler, priority) in sorted(drift_handlers.items()):
            lines.append(f"| {drift} | {handler} | {priority} |")

        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def discover_nagas() -> List[NagaManifest]:
    """Convenience function to discover all NAGAs."""
    scanner = NaradaScanner()
    return scanner.scan()


def get_naga_report() -> str:
    """Convenience function to get NAGA report."""
    scanner = NaradaScanner()
    scanner.scan()
    return scanner.generate_report()


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "NaradaScanner",
    "discover_nagas",
    "get_naga_report",
]
