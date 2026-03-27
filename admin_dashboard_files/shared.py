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

camera_cap = None

# ✅ ONLY TWO CAMERAS
available_camera_indices = [0, 1]

# ✅ FORCE STABLE BACKEND (BEST FOR WINDOWS)
camera_backends = {
    0: cv2.CAP_DSHOW,
    1: cv2.CAP_DSHOW
}

# =============================================================================
# CAMERA DETECTION (BACKGROUND)
# =============================================================================
def detect_cameras_bg():
    global available_camera_indices, camera_backends

    found = []
    backends = {}

    for i in range(2):  # ONLY CHECK 0 AND 1
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                found.append(i)
                backends[i] = cv2.CAP_DSHOW
            cap.release()

    if found:
        available_camera_indices = found
        camera_backends.update(backends)
    else:
        available_camera_indices = [0]
        camera_backends[0] = cv2.CAP_DSHOW

    print(f"[Camera] Verified indices: {available_camera_indices}")

threading.Thread(target=detect_cameras_bg, daemon=True).start()

# =============================================================================
# CAMERA CONTROL
# =============================================================================
def start_camera_stream(index=None):
    global camera_cap, current_camera_index

    if index is None:
        index = current_camera_index

    if camera_cap is not None and camera_cap.isOpened():
        return True

    print(f"[Camera] Starting camera {index}...")

    # ✅ FORCE DSHOW
    camera_cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if not camera_cap.isOpened():
        print(f"[Camera] Failed to open camera {index}")
        return False

    # Improve quality
    try:
        camera_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera_cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    except:
        pass

    return True


def release_camera_stream():
    global camera_cap
    if camera_cap:
        camera_cap.release()
    camera_cap = None


# ✅ FIXED SWITCHING (CRITICAL)
def switch_camera_live(index):
    global current_camera_index

    print(f"[Camera] Switching to camera {index}")

    current_camera_index = index

    # Step 1: Release current camera
    release_camera_stream()

    # Step 2: Small delay (important)
    time.sleep(0.3)

    # Step 3: Start new camera
    start_camera_stream(index)


# =============================================================================
# SETTINGS
# =============================================================================
current_camera_index = config_manager.get("camera_index") or 0

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