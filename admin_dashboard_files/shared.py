import cv2
from PIL import Image
import os
import sys
from datetime import datetime
import json
import numpy as np
import time
import threading

# PATH FIX for MODULAR DB
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Reduce OpenCV logs
try:
    cv2.setLogLevel(0)
except:
    pass

# DB imports (safe fallback)
try:
    from db import get_connection, get_student_by_regno, record_attendance
except:
    get_connection = lambda: None
    get_student_by_regno = lambda x: None
    record_attendance = lambda **k: None

# Load UI settings
import admin_dashboard_files.config_manager as config_manager

# =============================================================================
# GLOBALS
# =============================================================================

# =============================================================================
# CAMERA MANAGER (SEAMLESS SWITCHING)
# =============================================================================
class CameraManager:
    def __init__(self):
        self.pool = {}
        self.active_index = config_manager.get("camera_index") or 0
        self.is_running = True
        self.lock = threading.Lock()
        
    def warmup(self):
        """Initializes all available cameras in the background."""
        for i in [0, 1]:
            threading.Thread(target=self._init_camera, args=(i,), daemon=True).start()

    def _init_camera(self, index):
        try:
            # Try MSMF (Fastest) then DSHOW
            cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
            if not cap.isOpened():
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                with self.lock:
                    self.pool[index] = cap
                
                # Start a "drainer" for this specific camera to keep buffer fresh
                threading.Thread(target=self._drain_buffers, args=(index,), daemon=True).start()
                print(f"[Camera] {index} warmed up and draining.")
        except Exception as e:
            print(f"[Camera] Failed to init {index}: {e}")

    def _drain_buffers(self, index):
        """Constantly reads frames to ensure the 'next' read is live, not cached."""
        while self.is_running:
            with self.lock:
                cap = self.pool.get(index)
            if cap and cap.isOpened():
                # If this is the active camera, the UI loop will read it.
                # If NOT active, we must grab and discard to keep buffer fresh.
                if index != self.active_index:
                    try:
                        cap.grab() # grab() is lighter than read()
                    except:
                        pass
            time.sleep(0.01) # Small sleep to avoid CPU pin

    @property
    def camera_cap(self):
        """Returns the current active VideoCapture object."""
        with self.lock:
            cap = self.pool.get(self.active_index)
        if cap is None or not cap.isOpened():
            # Lazy re-init if needed
            self._init_camera(self.active_index)
            return None
        return cap

    def switch(self, index):
        print(f"[Camera] Instant switch to {index}")
        self.active_index = index
        return True

    def release_all(self):
        self.is_running = False
        with self.lock:
            for cap in self.pool.values():
                cap.release()
            self.pool.clear()

# Global Singleton
manager = CameraManager()
manager.warmup()

# Dynamics via Module-level __getattr__ (Python 3.7+)
def __getattr__(name):
    if name == "available_camera_indices":
        with manager.lock:
            return list(manager.pool.keys()) if manager.pool else [0, 1]
    if name == "current_camera_index":
        return manager.active_index
    if name == "camera_cap":
        return camera_cap_proxy
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Helper functions for backward compatibility
def start_camera_stream(index=None): 
    if index is not None: manager.active_index = index
    return manager.camera_cap is not None

def switch_camera_live(index): 
    return manager.switch(index)

def release_camera_stream(): 
    pass # We keep them warm

def release_all_cameras(): 
    manager.release_all()

# Export a dynamic-acting object for 'shared.camera_cap'
class SharedCameraProxy:
    def __getattr__(self, name):
        cap = manager.camera_cap
        if cap is not None: 
            return getattr(cap, name)
        raise AttributeError(f"Camera not ready for attribute '{name}'")
    
    def isOpened(self):
        cap = manager.camera_cap
        return cap is not None and cap.isOpened()
    
    def read(self):
        cap = manager.camera_cap
        if cap: return cap.read()
        return False, None

camera_cap_proxy = SharedCameraProxy()
# Note: we don't define 'camera_cap' here as a global because __getattr__ handles it


# =============================================================================
# SETTINGS
# =============================================================================
# current_camera_index is handled dynamically via __getattr__

# =============================================================================
# ATTENDANCE STATE (GLOBAL CACHE)
# =============================================================================
present_student_ids = set()
present_details_list = []
all_students_cache = []      # List of all registered students
total_students_count = 0     # Total count of registered students
sidebar_stats_callback = None

def sync_attendance_from_db():
    """Initializes present_student_ids and present_details_list from Today's DB records."""
    global present_student_ids, present_details_list
    try:
        from db import get_attendance_by_date
        today = datetime.now().strftime("%Y-%m-%d")
        records = get_attendance_by_date(today)
        
        new_present_ids = set()
        new_details_list = []
        
        # Latest should be at the bottom for the UI reversed list display
        for r in reversed(records):
            info = {
                'name': r['name'],
                'reg': r['reg_no'],
                'course': r['course'],
                'session': r['program'],
                'date': str(r['date']),
                'time': str(r['time_in'])
            }
            new_present_ids.add(r['reg_no'])
            new_details_list.append(info)
            
        present_student_ids.clear()
        present_student_ids.update(new_present_ids)
        
        present_details_list.clear()
        present_details_list.extend(new_details_list)
        return True
    except Exception as e:
        print(f"[Sync] Error synchronizing attendance: {e}")
        return False

def refresh_global_stats():
    """Syncs everything (attendance, total students, all students) from DB to cache."""
    global total_students_count, all_students_cache
    try:
        from db import get_all_students_minimal
        # 1. Sync Attendance
        sync_attendance_from_db()
        
        # 2. Sync Student Database
        all_students_cache = get_all_students_minimal()
        total_students_count = len(all_students_cache)
        
        # 3. Trigger UI callback if attached
        if sidebar_stats_callback:
            sidebar_stats_callback()
            
        return True
    except Exception as e:
        print(f"[Global Sync] Error: {e}")
        return False