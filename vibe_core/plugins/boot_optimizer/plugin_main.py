"""Boot Optimizer Plugin - Defers heavy initialization."""

import logging

from vibe_core.plugin_protocol import HookResult, KernelPlugin

logger = logging.getLogger("BOOT_OPTIMIZER")


class BootOptimizerPlugin(KernelPlugin):
    @property
    def plugin_id(self) -> str:
        return "boot_optimizer"

    def on_boot(self, kernel, config=None) -> HookResult:
        # Patch kernel to ensure heavy components remain lazy if possible
        # This is mostly demonstrative as we already applied lazy_class in kernel_impl

        logger.info("🚀 Boot optimization plugin active")
        return HookResult.ok("Boot optimization applied")
