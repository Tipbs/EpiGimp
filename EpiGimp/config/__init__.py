from pathlib import Path
import json

CONFIG_PATH = Path.home() / '.EpiGimprc'

DEFAULTS = {
    'window': {'width': 1200, 'height': 800},
    'recent_files': []
}

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
        return DEFAULTS.copy()




def save_settings(settings: dict):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
