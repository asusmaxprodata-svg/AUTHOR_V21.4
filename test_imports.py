#!/usr/bin/env python3
"""Test script to check for potential errors in core imports"""

from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

print("=== TESTING CORE IMPORTS ===")

# Test 1: Health Check
try:
    from core.health_check import HealthChecker
    print("✅ HealthChecker imported successfully")
except Exception as e:
    print(f"❌ HealthChecker import failed: {e}")

# Test 2: AI Signal
try:
    from core.ai_signal import _client
    print("✅ AI Signal imported successfully")
except Exception as e:
    print(f"❌ AI Signal import failed: {e}")

# Test 3: Config Manager
try:
    from core.config_manager import get_exchange
    print("✅ Config Manager imported successfully")
except Exception as e:
    print(f"❌ Config Manager import failed: {e}")

# Test 4: Data Pipeline
try:
    from core.data_pipeline import fetch_klines
    print("✅ Data Pipeline imported successfully")
except Exception as e:
    print(f"❌ Data Pipeline import failed: {e}")

# Test 5: Trade Executor
try:
    from core.trade_executor import place_order
    print("✅ Trade Executor imported successfully")
except Exception as e:
    print(f"❌ Trade Executor import failed: {e}")

# Test 6: Notifier
try:
    from core.notifier import send_telegram_message
    print("✅ Notifier imported successfully")
except Exception as e:
    print(f"❌ Notifier import failed: {e}")

print("\n=== TESTING ENVIRONMENT VARIABLES ===")
required_vars = [
    'BYBIT_API_KEY', 'BYBIT_API_SECRET', 'OPENAI_API_KEY', 
    'TELEGRAM_BOT_TOKEN', 'EXCHANGE', 'SYMBOL', 'MODE'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: SET")
    else:
        print(f"❌ {var}: NOT SET")

print("\n=== TESTING HEALTH CHECK ===")
try:
    from core.health_check import HealthChecker
    checker = HealthChecker()
    results = checker.run_all_checks()
    print(f"Health Check Status: {results.get('overall_status', 'unknown')}")
    
    # Show individual check results
    for check_name, result in results.get('checks', {}).items():
        status = result.get('status', 'unknown')
        print(f"  {check_name}: {status}")
        
except Exception as e:
    print(f"❌ Health check failed: {e}")

print("\n=== TESTING CONFIGURATION ===")
try:
    from core.config_manager import get_exchange, get_symbol, get_mode
    exchange = get_exchange()
    symbol = get_symbol()
    mode = get_mode()
    print(f"✅ Exchange: {exchange}")
    print(f"✅ Symbol: {symbol}")
    print(f"✅ Mode: {mode}")
except Exception as e:
    print(f"❌ Configuration test failed: {e}")

print("\n=== TESTING AI SIGNAL ===")
try:
    from core.ai_signal import _client
    client = _client()
    if client:
        print("✅ OpenAI client initialized successfully")
    else:
        print("⚠️ OpenAI client not available (API key may be missing)")
except Exception as e:
    print(f"❌ AI Signal test failed: {e}")

print("\n=== TESTING TELEGRAM ===")
try:
    from core.notifier import send_telegram_message
    # Don't actually send, just test import
    print("✅ Telegram notifier imported successfully")
except Exception as e:
    print(f"❌ Telegram test failed: {e}")

print("\n=== TEST COMPLETE ===")
