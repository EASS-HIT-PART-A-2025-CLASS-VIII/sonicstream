
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'seeding'))

from create_albums_table import create_albums_table

if __name__ == "__main__":
    try:
        create_albums_table()
    except Exception as e:
        print(f"Launcher Error: {e}")
