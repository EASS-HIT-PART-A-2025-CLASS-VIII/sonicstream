import os

def remove_zone_files():
    count = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'Zone.Identifier' in file:
                path = os.path.join(root, file)
                try:
                    os.remove(path)
                    print(f"Removed: {path}")
                    count += 1
                except Exception as e:
                    print(f"Error removing {path}: {e}")
    print(f"Total removed: {count}")

if __name__ == "__main__":
    remove_zone_files()
