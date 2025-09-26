#!/usr/bin/env python3
"""Test health check functionality"""

from dotenv import load_dotenv
load_dotenv()

from core.health_check import HealthChecker

print("=== TESTING HEALTH CHECK ===")
checker = HealthChecker()
results = checker.run_all_checks()

print(f"Health Status: {results.get('overall_status')}")
print("Individual checks:")
for k, v in results.get('checks', {}).items():
    print(f"  {k}: {v.get('status')}")

print("\n=== TESTING STREAMLIT STARTUP ===")
try:
    import streamlit as st
    print("✅ Streamlit imported successfully")
except Exception as e:
    print(f"❌ Streamlit import failed: {e}")

print("\n=== TESTING CORE MODULES ===")
modules_to_test = [
    'core.config_manager',
    'core.ai_signal', 
    'core.notifier',
    'core.trade_executor',
    'core.health_check'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module} imported successfully")
    except Exception as e:
        print(f"❌ {module} import failed: {e}")

print("\n=== TEST COMPLETE ===")
