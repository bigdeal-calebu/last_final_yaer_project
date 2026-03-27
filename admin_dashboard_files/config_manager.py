import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "system_settings.json")

# Sensible Defaults
DEFAULT_CONFIG = {
    # Camera Params
    "camera_index": 0,
    "process_every_n_frames": 1,
    "detection_scale": 0.75,
    
    # Recognition Params
    "confidence_threshold": 85,  # LBPH distance — lower is stricter; 85 is a good default
    "capture_unknowns": True,
    "unknown_frames_to_capture": 15,
    
    # Attendance / Reporting Params
    "late_arrival_time": "08:30:00",
    
    # UI Preference
    "appearance_mode": "Dark",
    
    # Archiver
    "last_archive_date": ""
}

_current_config = None

def load_config():
    """Load settings from JSON, inject defaults for missing keys."""
    global _current_config
    
    # Start with defaults
    config_data = dict(DEFAULT_CONFIG)
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_config = json.load(f)
                # Update with saved settings (only keys we know about)
                for k, v in saved_config.items():
                    if k in config_data:
                        config_data[k] = v
        except Exception as e:
            print(f"Warning: Could not read {CONFIG_FILE}, using defaults. Error: {e}")
            
    _current_config = config_data
    return _current_config

def get(key):
    """Retrieve a single config value."""
    if _current_config is None:
        load_config()
    return _current_config.get(key, DEFAULT_CONFIG.get(key))

def set_val(key, value):
    """Set a single config value in memory."""
    if _current_config is None:
        load_config()
    _current_config[key] = value

def set(key, value):
    """Set a single config value and persist to file."""
    set_val(key, value)
    save_config()

def save_config():
    """Persist the current in-memory config dict down to the JSON file."""
    if _current_config is None:
        return
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(_current_config, f, indent=4)
        print("System Settings successfully saved.")
    except Exception as e:
        print(f"Failed to save {CONFIG_FILE}: {e}")

# Load immediately on import
load_config()
