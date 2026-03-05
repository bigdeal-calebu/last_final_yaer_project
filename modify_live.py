import sys
import importlib
import os

# Store the callback to rebuild the current view
_current_refresh_action = lambda: print("[Live Modify] No refresh action registered.")

def set_refresh_action(action_func):
    """
    Register the function that will be called to redraw the UI.
    """
    global _current_refresh_action
    _current_refresh_action = action_func

def trigger_live_refresh():
    """
    Reloads all modified project modules and redraws the current screen.
    """
    print("\n[Live Modify] Triggering Live Refresh...")
    
    # Identify the root directory of the project
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We must collect the modules first to avoid dictionary size change during iteration
    modules_to_reload = []
    
    for mod_name, mod in list(sys.modules.items()):
        # Only reload modules that exist as files inside our project directory
        mod_file = getattr(mod, '__file__', None)
        if mod and mod_file and mod_file.startswith(project_dir):
            if "modify_live" not in mod_name and "main" not in mod_name:
                modules_to_reload.append((mod_name, mod))
                
    # Reload the modules in the order they're found (might need multiple passes for complex dependencies
    # but a simple iteration usually catches UI tweaks perfectly).
    for mod_name, mod in modules_to_reload:
        try:
            importlib.reload(mod)
            print(f"  [+] Reloaded: {mod_name}")
        except Exception as e:
            print(f"  [-] Failed to reload {mod_name}: {e}")
            
    print("[Live Modify] Rebuilding UI...")
    # Call the registered redraw action (clears screen, builds new components)
    _current_refresh_action()
    print("[Live Modify] Refresh Complete.\n")
