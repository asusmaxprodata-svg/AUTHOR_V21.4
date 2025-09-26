# core/import_fixes.py
"""
Import fixes and fallback mechanisms for core modules
Mengatasi masalah import yang menyebabkan crash saat deployment
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict

# Add current directory to Python path
if "." not in sys.path:
    sys.path.insert(0, ".")


def safe_import(module_name: str, fallback=None):
    """Safely import a module with fallback"""
    try:
        return __import__(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return fallback


def safe_getattr(obj, attr, default=None):
    """Safely get attribute with fallback"""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def safe_call(func, *args, **kwargs):
    """Safely call a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Warning: Function call failed: {e}")
        return None


# Fallback logger
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


def get_logger(name: str):
    """Get logger with fallback"""
    try:
        from core.logger import get_logger as _get_logger

        return _get_logger(name)
    except ImportError:
        return FallbackLogger(name)


def load_json(path: str, default: Any = None) -> Any:
    """Load JSON with fallback"""
    try:
        import json

        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: str, obj: Any) -> bool:
    """Save JSON with error handling"""
    try:
        import json

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save JSON to {path}: {e}")
        return False


def get_exchange() -> str:
    """Get exchange with fallback"""
    try:
        from core.config_manager import get_exchange as _get_exchange

        return _get_exchange()
    except ImportError:
        # Fallback to environment variable or default
        return os.getenv("EXCHANGE", "bybit")


def get_binance_testnet() -> bool:
    """Get Binance testnet setting with fallback"""
    try:
        from core.config_manager import (
            get_binance_testnet as _get_binance_testnet
        )

        return _get_binance_testnet()
    except ImportError:
        # Fallback to environment variable or default
        return os.getenv("BINANCE_TESTNET", "true").lower() in (
            "true", "1", "yes"
        )


def check_websocket_connection(
    host: str = "localhost", port: int = 8765, timeout: int = 5
) -> bool:
    """Check WebSocket connection with fallback"""
    try:
        from websocket import create_connection

        ws = create_connection(f"ws://{host}:{port}", timeout=timeout)
        ws.close()
        return True
    except Exception:
        return False


def check_api_connectivity(url: str, timeout: int = 10) -> bool:
    """Check API connectivity with fallback"""
    try:
        import requests

        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def get_system_info() -> Dict[str, Any]:
    """Get system information with fallback"""
    try:
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": (
                psutil.disk_usage("/").percent
                if os.name != "nt"
                else psutil.disk_usage("C:\\").percent
            ),
        }
    except ImportError:
        return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}


def validate_config_files() -> Dict[str, Any]:
    """Validate configuration files with fallback"""
    required_configs = [
        "config/global.json",
        "config/scalping.json",
        "config/adaptive.json",
    ]

    results = {"valid": True, "missing": [], "errors": []}

    for config_path in required_configs:
        if not Path(config_path).exists():
            results["missing"].append(config_path)
            results["valid"] = False
        else:
            try:
                load_json(config_path)
            except Exception as e:
                results["errors"].append(f"{config_path}: {e}")
                results["valid"] = False

    return results


def get_process_info() -> Dict[str, Any]:
    """Get process information with fallback"""
    try:
        import psutil

        processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if "python" in proc.info["name"].lower():
                    cmdline = " ".join(proc.info["cmdline"])
                    if any(
                        keyword in cmdline
                        for keyword in ["run.py", "kang_bot", "streamlit"]
                    ):
                        processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cmdline": (
                                    cmdline[:100] + "..."
                                    if len(cmdline) > 100
                                    else cmdline
                                ),
                            }
                        )
            except Exception:
                continue
        return {"processes": processes, "count": len(processes)}
    except ImportError:
        return {"processes": [], "count": 0}


def check_log_files() -> Dict[str, Any]:
    """Check log files with fallback"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"exists": False, "files": []}

        log_files = list(log_dir.glob("*.log"))
        return {
            "exists": True,
            "files": [f.name for f in log_files],
            "count": len(log_files),
        }
    except Exception:
        return {"exists": False, "files": [], "count": 0}
