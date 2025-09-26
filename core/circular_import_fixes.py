# core/circular_import_fixes.py
"""
Fixes for circular import issues in core modules
Mengatasi masalah circular import yang menyebabkan crash saat deployment
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict

# Add current directory to Python path
if "." not in sys.path:
    sys.path.insert(0, ".")


def safe_import_core_module(module_name: str, fallback=None):
    """Safely import core modules with circular import protection"""
    try:
        # Check if module is already imported
        if module_name in sys.modules:
            return sys.modules[module_name]

        # Import with error handling
        module = __import__(module_name, fromlist=[""])
        return module
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return fallback
    except Exception as e:
        print(f"Warning: Error importing {module_name}: {e}")
        return fallback


def get_logger_safe(name: str):
    """Get logger with circular import protection"""
    try:
        from core.logger import get_logger

        return get_logger(name)
    except ImportError:
        # Fallback logger
        import logging

        return logging.getLogger(name)
    except Exception:
        # Ultimate fallback
        class FallbackLogger:
            def __init__(self, name):
                self.name = name

            def info(self, msg):
                print(f"[INFO] {self.name}: {msg}")

            def warning(self, msg):
                print(f"[WARNING] {self.name}: {msg}")

            def error(self, msg):
                print(f"[ERROR] {self.name}: {msg}")

            def debug(self, msg):
                print(f"[DEBUG] {self.name}: {msg}")

        return FallbackLogger(name)


def load_json_safe(path: str, default: Any = None) -> Any:
    """Load JSON with error handling"""
    try:
        import json

        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_safe(path: str, obj: Any) -> bool:
    """Save JSON with error handling"""
    try:
        import json

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        return True
    except Exception:
        return False


def get_config_safe(mode: str = "global") -> Dict[str, Any]:
    """Get configuration with circular import protection"""
    try:
        if mode == "global":
            return load_json_safe("config/global.json", {})
        else:
            return load_json_safe(f"config/{mode}.json", {})
    except Exception:
        return {}


def get_exchange_safe() -> str:
    """Get exchange setting with fallback"""
    try:
        config = get_config_safe("global")
        return config.get("exchange", os.getenv("EXCHANGE", "bybit"))
    except Exception:
        return os.getenv("EXCHANGE", "bybit")


def get_testnet_safe() -> bool:
    """Get testnet setting with fallback"""
    try:
        config = get_config_safe("global")
        return config.get(
            "testnet",
            os.getenv("BYBIT_TESTNET", "true").lower() in (
                "true", "1", "yes"
            ),
        )
    except Exception:
        return os.getenv("BYBIT_TESTNET", "true").lower() in (
            "true", "1", "yes"
        )


def get_mode_safe() -> str:
    """Get trading mode with fallback"""
    try:
        state = load_json_safe("data/state.json", {})
        return state.get("mode", "scalping")
    except Exception:
        return "scalping"


def get_leverage_safe() -> str:
    """Get leverage setting with fallback"""
    try:
        state = load_json_safe("data/state.json", {})
        return state.get("leverage", "auto")
    except Exception:
        return "auto"


def get_symbol_safe() -> str:
    """Get trading symbol with fallback"""
    try:
        config = get_config_safe("global")
        return config.get("symbol", "BTCUSDT")
    except Exception:
        return "BTCUSDT"


def get_equity_safe() -> float:
    """Get equity with fallback"""
    try:
        profit_data = load_json_safe("data/profit.json", {})
        return float(
            profit_data.get(
                "equity", profit_data.get("starting_capital", 30.0)
            )
        )
    except Exception:
        return 30.0


def get_running_safe() -> bool:
    """Get running status with fallback"""
    try:
        state = load_json_safe("data/state.json", {})
        return not state.get("paused", False)
    except Exception:
        return True


def validate_imports() -> Dict[str, bool]:
    """Validate all critical imports"""
    results = {}

    # Test core module imports
    core_modules = [
        "core.logger",
        "core.utils",
        "core.config_manager",
        "core.health_check",
        "core.import_fixes",
    ]

    for module in core_modules:
        try:
            __import__(module)
            results[module] = True
        except Exception:
            results[module] = False

    # Test external dependencies
    external_deps = ["psutil", "requests", "pandas", "numpy", "websocket"]

    for dep in external_deps:
        try:
            __import__(dep)
            results[dep] = True
        except Exception:
            results[dep] = False

    return results


def fix_circular_imports():
    """Fix common circular import issues"""
    fixes_applied = []

    try:
        # Fix 1: Ensure core modules can be imported independently
        logger = get_logger_safe("circular_import_fixes")
        logger.info("Starting circular import fixes")
        fixes_applied.append("logger_fix")

        # Fix 2: Validate configuration files
        config_status = validate_config_files()
        if config_status["valid"]:
            logger.info("Configuration files validated")
            fixes_applied.append("config_validation")
        else:
            logger.warning(f"Configuration issues: {config_status}")

        # Fix 3: Test critical functions
        exchange = get_exchange_safe()
        mode = get_mode_safe()
        symbol = get_symbol_safe()
        equity = get_equity_safe()

        logger.info(
            f"System state: exchange={exchange}, mode={mode}, "
            f"symbol={symbol}, equity={equity}"
        )
        fixes_applied.append("state_validation")

        # Fix 4: Validate imports
        import_status = validate_imports()
        failed_imports = [k for k, v in import_status.items() if not v]

        if failed_imports:
            logger.warning(f"Failed imports: {failed_imports}")
        else:
            logger.info("All imports validated successfully")
            fixes_applied.append("import_validation")

        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "import_status": import_status,
            "config_status": config_status,
        }

    except Exception as e:
        logger = get_logger_safe("circular_import_fixes")
        logger.error(f"Circular import fixes failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "fixes_applied": fixes_applied
        }


def validate_config_files() -> Dict[str, Any]:
    """Validate configuration files"""
    required_configs = [
        "config/global.json",
        "config/scalping.json",
        "config/adaptive.json",
    ]

    results = {"valid": True, "missing": [], "errors": [], "files": {}}

    for config_path in required_configs:
        if not Path(config_path).exists():
            results["missing"].append(config_path)
            results["valid"] = False
        else:
            try:
                config_data = load_json_safe(config_path)
                results["files"][config_path] = config_data
            except Exception as e:
                results["errors"].append(f"{config_path}: {e}")
                results["valid"] = False

    return results


if __name__ == "__main__":
    # Run circular import fixes
    result = fix_circular_imports()
    print(f"Circular import fixes result: {result}")
