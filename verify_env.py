"""
RehabAI - Pre-flight environment check.
Run with: .venv311\Scripts\python.exe verify_env.py
"""
import sys
import os
os.environ["PYTHONUTF8"] = "1"

print(f"Python: {sys.version}")
print()

checks = [
    ("streamlit",        "streamlit"),
    ("plotly",           "plotly"),
    ("pandas",           "pandas"),
    ("numpy",            "numpy"),
    ("mediapipe",        "mediapipe"),
    ("opencv-python",    "cv2"),
    ("scikit-learn",     "sklearn"),
    ("scipy",            "scipy"),
    ("joblib",           "joblib"),
    ("requests",         "requests"),
    ("firebase-admin",   "firebase_admin"),
    ("python-dotenv",    "dotenv"),
    ("Pillow",           "PIL"),
]

passed = 0
failed = 0
for pkg_name, import_name in checks:
    try:
        mod = __import__(import_name)
        ver = getattr(mod, "__version__", "?")
        print(f"  [OK]  {pkg_name:<20} -> {ver}")
        passed += 1
    except ImportError as e:
        print(f"  [XX]  {pkg_name:<20} -> MISSING  ({e})")
        failed += 1

print()
print(f"Result: {passed} passed, {failed} failed")
if failed == 0:
    print("Environment is COMPLETE -- ready to run the patient frontend.")
else:
    print("Fix the missing packages before launching the app.")
