from pathlib import Path
from typing import List
import importlib

class PluginManager:
    def __init__(self, plugin_dirs=None):
        self.plugin_dirs = plugin_dirs or [Path.cwd() / 'plugins']
        self.plugins = []


    def discover(self) -> List[Path]:
        found = []
        for d in self.plugin_dirs:
            d = Path(d)
            if not d.exists():
                continue
            for py in d.glob('*.py'):
                found.append(py)
        return found


    def load(self):
        for p in self.discover():
            try:
                spec = importlib.util.spec_from_file_location(p.stem, str(p))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.plugins.append(mod)
            except Exception as e:
                print('Failed to load plugin', p, e)
