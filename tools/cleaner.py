import streamlit as st
import os
import shutil
import platform
import ctypes
import math

def get_free_space_gb():
    """Returns the free space of C: drive in GB."""
    try:
        total, used, free = shutil.disk_usage("C:/")
        return round(free / (2**30), 2)  # Convert bytes to GB
    except Exception:
        return 0.0

def empty_recycle_bin():
    """
    Empties the Windows Recycle Bin using ctypes (no extra pip install needed).
    Returns True if successful.
    """
    if platform.system() != "Windows":
        return False
    try:
        # SHEmptyRecycleBinW arguments: (hwnd, root_path, flags)
        # Flags: 0x00000001 (No Sound), 0x00000002 (No Confirmation), 0x00000004 (No Progress UI)
        SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
        result = SHEmptyRecycleBin(None, None, 7) 
        return result == 0  # 0 means success
    except Exception:
        return False

def clean_directory(folder_path, progress_bar, status_text, current_step, total_steps):
    """
    Safely cleans a directory and updates the UI progress.
    """
    if not os.path.exists(folder_path):
        return 0, 0

    deleted_files = 0
    errors = 0
    
    # Get list of all files first to calculate precise progress
    try:
        all_items = os.listdir(folder_path)
    except PermissionError:
        return 0, 1  # Cannot access folder

    # Loop through items
    for index, item in enumerate(all_items):
        item_path = os.path.join(folder_path, item)
        
        # Update Status Text (Visual feedback for user)
        status_text.text(f"Scanning: {item[:30]}...") 
        
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Delete file
                deleted_files += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete folder
                deleted_files += 1
        except Exception:
            # If file is in use (Permission Denied), we just skip it
            errors += 1
            
        # Update Progress Bar dynamically
        # Logic: Base progress + (fraction of this folder * weight)
        step_progress = current_step / total_steps
        folder_progress = (index + 1) / len(all_items)
        total_progress = step_progress + (folder_progress / total_steps)
        
        # Cap at 1.0 to prevent errors
        progress_bar.progress(min(total_progress, 1.0))
        
    return deleted_files, errors

def run_tool():
    st.subheader("🧹 Pro System Deep Clean")
    st.caption("Cleans: %TEMP%, Windows Temp, Prefetch, and Recycle Bin.")
    
    # 1. Show Current Storage
    col1, col2 = st.columns(2)
    start_space = get_free_space_gb()
    
    with col1:
        st.metric(label="Current Free Space (C:)", value=f"{start_space} GB")
    
    with col2:
        if st.button("🚀 Start Deep Clean", type="primary"):
            
            # PREPARATION
            user_temp = os.environ.get('TEMP')
            system_temp = r"C:\Windows\Temp"
            prefetch = r"C:\Windows\Prefetch"
            
            paths_to_clean = [user_temp]
            
            # Add Windows System folders only if on Windows
            if platform.system() == "Windows":
                paths_to_clean.append(system_temp)
                paths_to_clean.append(prefetch)
            
            # UI ELEMENTS
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_box = st.expander("View Detailed Log", expanded=True)
            
            total_deleted = 0
            total_errors = 0
            
            # --- PHASE 1: FILE CLEANING ---
            for i, path in enumerate(paths_to_clean):
                if path:
                    status_text.markdown(f"**Cleaning:** `{path}`")
                    d, e = clean_directory(path, progress_bar, status_text, i, len(paths_to_clean) + 1)
                    total_deleted += d
                    total_errors += e
                    with log_box:
                        if e > 0:
                            st.caption(f"⚠️ `{path}`: Removed {d} files. Skipped {e} (In Use).")
                        else:
                            st.caption(f"✅ `{path}`: Fully Cleaned.")

            # --- PHASE 2: RECYCLE BIN ---
            status_text.text("Emptying Recycle Bin...")
            if empty_recycle_bin():
                 with log_box:
                    st.caption("🗑️ Recycle Bin: Emptied Successfully.")
            else:
                 with log_box:
                    st.caption("ℹ️ Recycle Bin: Already empty or permission denied.")
            
            progress_bar.progress(100)
            
            # --- RESULTS ---
            end_space = get_free_space_gb()
            space_saved = round(end_space - start_space, 2)
            
            st.divider()
            st.balloons()
            
            # Final Report Card
            res_col1, res_col2, res_col3 = st.columns(3)
            with res_col1:
                st.metric("Files Removed", value=total_deleted)
            with res_col2:
                st.metric("New Free Space", value=f"{end_space} GB", delta=f"+{space_saved} GB")
            with res_col3:
                 st.success("System Optimized! 🚀")
            
            st.warning("Note: Files currently in use by open apps were safely skipped.")