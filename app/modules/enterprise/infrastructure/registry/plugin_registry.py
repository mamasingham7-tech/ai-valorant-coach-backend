import structlog
from typing import Dict

logger = structlog.get_logger()

class PluginSDK:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, PluginSDK] = {}

    def register_plugin(self, plugin: PluginSDK) -> None:
        """Registers a dynamic plugin checking metadata version formats."""
        if not plugin.name or not plugin.version:
            raise ValueError("Plugin metadata missing name or version.")
            
        logger.info("Registering plugin", name=plugin.name, version=plugin.version)
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> PluginSDK:
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found in registry.")
        return self._plugins[name]

    def list_plugins(self) -> Dict[str, str]:
        return {name: p.version for name, p in self._plugins.items()}

# Global Plugin Registry
plugin_registry = PluginRegistry()
