import sys
import os
import subprocess

print("-" * 50)
print("DEBUGGING TEST ENVIRONMENT")
print("-" * 50)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

def install_deps():
    print("\nInstalling/Updating dependencies...")
    try:
        # Using sys.executable to ensure we install into the CURRENTLY running environment
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                             "passlib[bcrypt]", "pytest", "sqlalchemy", 
                             "python-jose[cryptography]", "python-multipart",
                             "fastapi", "httpx", "psycopg[binary]"])
        print("✅ Dependencies installed successfully.")
    except Exception as e:
        print(f"❌ Installation failed: {e}")

# Try imports and collect missing ones
missing = []
for mod in ["passlib", "pytest", "sqlalchemy", "jose", "multipart", "fastapi", "httpx", "psycopg"]:
    try:
        __import__(mod)
        print(f"✅ {mod} is available.")
    except ImportError:
        print(f"❌ {mod} is MISSING.")
        missing.append(mod)

if missing:
    install_deps()

print("-" * 50)
print("FINAL RUN CHECK")
print("-" * 50)

# Add current directory to path so 'app' can be found
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

try:
    import pytest
    args = ["tests/test_api_mock.py", "-v"]
    print(f"Running: pytest {' '.join(args)}")
    sys.exit(pytest.main(args))
except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)
