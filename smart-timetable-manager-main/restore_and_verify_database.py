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

    source_path = os.path.expanduser("~/edunova.db")
    backup_path = os.path.expanduser("~/edunova.db.backup_original")
    dest_dir = os.path.expanduser("~/cep-project/smart-timetable-manager-main/backend")
    dest_path = os.path.join(dest_dir, "edunova.db")

    # Step 1: Verify Source Database Exists
    print("\n[Step 1] Inspecting Source Database...")
    print(f"  Source path: {source_path}")
    if not os.path.exists(source_path):
        print(f"  [ERROR] Source database not found at {source_path}")
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

    # Step 2: Create Backup of Source
    print("\n[Step 2] Creating Source Backup...")
    shutil.copy2(source_path, backup_path)
    bak_size = os.path.getsize(backup_path)
    bak_hash = calculate_sha256(backup_path)
    print(f"  Backup saved to: {backup_path}")
    print(f"  Backup hash:     {bak_hash}")
    assert src_hash == bak_hash, "Backup hash mismatch!"
    print("  [PASS] Source backup created and verified.")

    # Step 3: Copy to Destination
    print("\n[Step 3] Placing Database into Backend Directory...")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    dest_size = os.path.getsize(dest_path)
    dest_hash = calculate_sha256(dest_path)
    print(f"  Destination: {dest_path}")
    print(f"  Dest size:   {dest_size} bytes")
    print(f"  Dest hash:   {dest_hash}")

    assert src_hash == dest_hash, "Destination hash mismatch!"
    print("  [PASS] Hashes match bit-for-bit between source and destination.")

    dest_integrity, dest_counts = verify_sqlite_db(dest_path)
    assert dest_integrity == "ok", "Destination integrity check failed!"
    assert dest_counts["timetable"] == 135, "Destination timetable count mismatch!"
    assert dest_counts["faculty"] == 24, "Destination faculty count mismatch!"
    print("  [PASS] Destination database verified healthy and fully intact.")

    # Step 4: Confirm Original Still Exists
    print("\n[Step 4] Checking Original File Preservation...")
    if os.path.exists(source_path):
        print(f"  [PASS] Original source file at {source_path} is preserved and untouched.")

    print("\n" + "=" * 65)
    print("   DATABASE PLACEMENT AND VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
