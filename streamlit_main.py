# Auto-generated streamlit entrypoint (build 7a0df6abee) - Enhanced
# Tries dashboard.app first, then streamlit_app.app
import os
import sys
import importlib
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
# Ensure local packages are importable
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Add current directory to Python path for imports
sys.path.append(".")

# Wait for dependencies to be ready (for container startup) - ENHANCED
time.sleep(2)

# Set environment variables for deployment
os.environ.setdefault("PYTHONPATH", f"{ROOT}:.")
os.environ.setdefault("TZ", "Asia/Jakarta")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Enhanced error handling and fallback
candidates = [
    ("dashboard.app", "dashboard/app.py"),
    ("streamlit_app.app", "streamlit_app/app.py"),
]

found = None
error_messages = []

for modname, hint in candidates:
    try:
        # Check if module exists
        if not os.path.exists(hint):
            error_messages.append(f"{modname}: File {hint} not found")
            continue

        # Try to import
        importlib.import_module(modname)
        found = modname
        break
    except Exception as e:
        error_messages.append(f"{modname}: {str(e)}")
        continue

if not found:
    import streamlit as st

    st.set_page_config(page_title="Error", page_icon="❌", layout="wide")
    st.error("❌ Tidak menemukan entrypoint Streamlit yang valid.")
    st.write("**Candidates yang dicoba:**")
    for modname, hint in candidates:
        st.write(f"- {modname} ({hint})")

    st.write("**Error messages:**")
    for msg in error_messages:
        st.write(f"- {msg}")

    st.write("**Troubleshooting:**")
    st.write("1. Pastikan file `dashboard/app.py` atau `streamlit_app/app.py` ada")
    st.write("2. Check jika ada error di import modules")
    st.write("3. Verify dependencies sudah terinstall dengan benar")
    st.write("4. Check logs container untuk detail error")

    # Don't stop, let it run to show error page
else:
    # Re-run the selected module
    import runpy

    pkg, _, _ = found.partition(".")
    # Add candidate packages to sys.path for nested imports
    pkg_path = os.path.join(ROOT, pkg)
    if os.path.isdir(pkg_path) and pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

    try:
        runpy.run_module(found, run_name="__main__")
    except Exception as e:
        import streamlit as st

        st.set_page_config(page_title="Runtime Error", page_icon="❌", layout="wide")
        st.error(f"❌ Runtime error saat menjalankan {found}: {str(e)}")
        st.write("**Detail error:**")
        import traceback

        st.code(traceback.format_exc())
