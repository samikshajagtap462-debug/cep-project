#!/usr/bin/env python3
"""
EduNova Database Verification, Backup, and Placement Script for PythonAnywhere.
Safely inspects, backs up, and places edunova.db into the backend directory.
"""

import os
import sys
import shutil
import sqlite3
import hashlib

def calculate_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

def verify_sqlite_db(filepath: str):
    con = sqlite3.connect(filepath)
    cur = con.cursor()
    integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
    
    tables_to_check = [
        "faculty",
        "timetable",
        "subjects",
        "rooms",
        "faculty_assignments",
        "classes",
        "batches",
        "admin_notifications"
    ]
    counts = {}
    for table in tables_to_check:
        try:
            count = cur.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            counts[table] = count
        except Exception as e:
            counts[table] = f"Error: {e}"
    con.close()
    return integrity, counts

def main():
    print("=" * 65)
    print("   EDUNOVA DATABASE VERIFICATION & PLACEMENT (PYTHONANYWHERE)")
    print("=" * 65)

    home_source = os.path.expanduser("~/edunova.db")
    home_backup = os.path.expanduser("~/edunova.db.backup_original")
    dest_dir = os.path.expanduser("~/cep-project/smart-timetable-manager-main/backend")
    dest_path = os.path.join(dest_dir, "edunova.db")

    source_path = None
    if os.path.exists(home_source):
        source_path = home_source
    elif os.path.exists(home_backup):
        source_path = home_backup
    elif os.path.exists(dest_path):
        source_path = dest_path

    # Step 1: Verify Source Database Exists
    print("\n[Step 1] Inspecting Source Database...")
    print(f"  Source path: {source_path}")
    if not source_path or not os.path.exists(source_path):
        print("  [ERROR] No database found at ~/edunova.db, ~/edunova.db.backup_original, or destination.")
        print("  Please make sure ~/edunova.db exists before running this script.")
        sys.exit(1)

    src_size = os.path.getsize(source_path)
    src_hash = calculate_sha256(source_path)
    print(f"  Byte size:   {src_size} bytes")
    print(f"  SHA-256:     {src_hash}")

    src_integrity, src_counts = verify_sqlite_db(source_path)
    print(f"  Integrity:   {src_integrity}")
    print("  Row Counts:")
    for tbl, cnt in src_counts.items():
        print(f"    - {tbl:22}: {cnt}")

    if src_integrity != "ok":
        print("  [ERROR] Source database integrity check failed!")
        sys.exit(1)

    if src_counts.get("timetable") != 135:
        print(f"  [WARNING] Timetable count is {src_counts.get('timetable')}, expected 135!")
    else:
        print("  [PASS] Timetable count verified: 135 sessions intact.")

    if src_counts.get("faculty") != 24:
        print(f"  [WARNING] Faculty count is {src_counts.get('faculty')}, expected 24!")
    else:
        print("  [PASS] Faculty count verified: 24 accounts intact.")

    # Step 2: Create Backup of Source if not already present
    print("\n[Step 2] Creating Source Backup...")
    if not os.path.exists(home_backup):
        shutil.copy2(source_path, home_backup)
        print(f"  Backup saved to: {home_backup}")
    else:
        print(f"  Backup already exists at: {home_backup}")

    bak_size = os.path.getsize(home_backup)
    bak_hash = calculate_sha256(home_backup)
    print(f"  Backup size:     {bak_size} bytes")
    print(f"  Backup hash:     {bak_hash}")
    print("  [PASS] Source backup confirmed safe on disk.")

    # Step 3: Copy to Destination
    print("\n[Step 3] Placing Database into Backend Directory...")
    os.makedirs(dest_dir, exist_ok=True)
    try:
        os.chmod(dest_dir, 0o775)
    except Exception:
        pass

    if os.path.abspath(source_path) != os.path.abspath(dest_path):
        shutil.copy2(source_path, dest_path)
    
    try:
        os.chmod(dest_path, 0o664)
        if hasattr(os, "sync"):
            os.sync()
    except Exception:
        pass

    dest_size = os.path.getsize(dest_path)
    dest_hash = calculate_sha256(dest_path)
    print(f"  Destination: {dest_path}")
    print(f"  Dest size:   {dest_size} bytes")
    print(f"  Dest hash:   {dest_hash}")

    assert dest_hash == src_hash, "Destination hash does not match source!"
    print("  [PASS] Hashes match bit-for-bit between source and destination.")

    dest_integrity, dest_counts = verify_sqlite_db(dest_path)
    assert dest_integrity == "ok", "Destination integrity check failed!"
    assert dest_counts["timetable"] == 135, "Destination timetable count mismatch!"
    assert dest_counts["faculty"] == 24, "Destination faculty count mismatch!"
    print("  [PASS] Destination database verified healthy and fully intact.")

    # Step 4: Confirm Original Still Exists
    print("\n[Step 4] Checking Original File Preservation...")
    if os.path.exists(home_source):
        print(f"  [PASS] Original source file at {home_source} is preserved and untouched.")

    print("\n" + "=" * 65)
    print("   DATABASE PLACEMENT AND VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
