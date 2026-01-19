
import os
import glob

files_to_remove = [
    "backend/analyze_db.py",
    "backend/check_corr.py",
    "backend/check_pop.py",
    "backend/check_raw_pop.py",
    "backend/debug_tests.py",
    "backend/launcher.py",
    "backend/launcher_corr.py",
    "backend/launcher_raw.py",
    "backend/pop_results.txt"
]

for f in files_to_remove:
    if os.path.exists(f):
        try:
            os.remove(f)
            print(f"Removed {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")
    else:
        print(f"File {f} does not exist")
