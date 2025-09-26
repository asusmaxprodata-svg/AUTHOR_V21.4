# core/env_validation.py
"""
Environment variables validation and fallback mechanisms
Mengatasi masalah environment variables yang menyebabkan crash saat deployment
"""

import os
# import sys  # Unused import
from pathlib import Path
from typing import Any, Dict


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}

    if not Path(env_path).exists():
        return env_vars

    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

    return env_vars


def get_env_var(key: str, default: Any = None, required: bool = False) -> Any:
    """Get environment variable with fallback and validation - ENHANCED"""
    value = os.getenv(key, default)

    if required and value is None:
        # Don't crash during deployment, use fallback instead
        print(
            f"Warning: Required environment variable {key} is not set, "
            f"using fallback"
        )
        return default

    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "y", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable"""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


def validate_exchange_config() -> Dict[str, Any]:
    """Validate exchange configuration"""
    results = {"valid": True, "exchange": None, "errors": [], "warnings": []}

    # Get exchange type
    exchange = get_env_var("EXCHANGE", "bybit")
    results["exchange"] = exchange

    if exchange == "bybit":
        # Validate Bybit configuration
        api_key = get_env_var("BYBIT_API_KEY")
        api_secret = get_env_var("BYBIT_API_SECRET")
        testnet = get_env_bool("BYBIT_TESTNET", True)

        if not api_key or api_key == "your_bybit_api_key_here":
            results["errors"].append(
                "BYBIT_API_KEY not set or using default value"
            )
            results["valid"] = False

        if not api_secret or api_secret == "your_bybit_api_secret_here":
            results["errors"].append(
                "BYBIT_API_SECRET not set or using default value"
            )
            results["valid"] = False

        results["bybit_testnet"] = testnet

    elif exchange == "binance":
        # Validate Binance configuration
        api_key = get_env_var("BINANCE_API_KEY")
        api_secret = get_env_var("BINANCE_API_SECRET")
        testnet = get_env_bool("BINANCE_TESTNET", True)

        if not api_key or api_key == "your_binance_api_key_here":
            results["errors"].append("BINANCE_API_KEY not set or using default value")
            results["valid"] = False

        if not api_secret or api_secret == "your_binance_api_secret_here":
            results["errors"].append(
                "BINANCE_API_SECRET not set or using default value"
            )
            results["valid"] = False

        results["binance_testnet"] = testnet

    return results


def validate_openai_config() -> Dict[str, Any]:
    """Validate OpenAI configuration"""
    results = {"valid": True, "errors": [], "warnings": []}

    api_key = get_env_var("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        results["errors"].append("OPENAI_API_KEY not set or using default value")
        results["valid"] = False
    else:
        # Basic validation - check if it starts with 'sk-'
        if not api_key.startswith("sk-"):
            results["warnings"].append("OPENAI_API_KEY format may be incorrect")

    return results


def validate_telegram_config() -> Dict[str, Any]:
    """Validate Telegram configuration"""
    results = {"valid": True, "errors": [], "warnings": []}

    bot_token = get_env_var("TELEGRAM_BOT_TOKEN")
    admin_user_id = get_env_var("TELEGRAM_ADMIN_USER_ID")

    if not bot_token or bot_token == "your_telegram_bot_token_here":
        results["errors"].append("TELEGRAM_BOT_TOKEN not set or using default value")
        results["valid"] = False

    if not admin_user_id or admin_user_id == "your_telegram_user_id_here":
        results["errors"].append(
            "TELEGRAM_ADMIN_USER_ID not set or using default value"
        )
        results["valid"] = False
    else:
        # Validate user ID is numeric
        try:
            int(admin_user_id)
        except ValueError:
            results["warnings"].append("TELEGRAM_ADMIN_USER_ID should be numeric")

    return results


def validate_whatsapp_config() -> Dict[str, Any]:
    """Validate WhatsApp/Twilio configuration (optional)"""
    results = {"valid": True, "errors": [], "warnings": [], "optional": True}

    account_sid = get_env_var("TWILIO_ACCOUNT_SID")
    auth_token = get_env_var("TWILIO_AUTH_TOKEN")
    phone_number = get_env_var("TWILIO_PHONE_NUMBER")

    if not account_sid or account_sid == "your_twilio_account_sid_here":
        results["warnings"].append("TWILIO_ACCOUNT_SID not set (optional)")

    if not auth_token or auth_token == "your_twilio_auth_token_here":
        results["warnings"].append("TWILIO_AUTH_TOKEN not set (optional)")

    if not phone_number or phone_number == "your_twilio_phone_number_here":
        results["warnings"].append("TWILIO_PHONE_NUMBER not set (optional)")

    return results


def validate_all_env() -> Dict[str, Any]:
    """Validate all environment variables"""
    results = {
        "overall_valid": True,
        "exchange": validate_exchange_config(),
        "openai": validate_openai_config(),
        "telegram": validate_telegram_config(),
        "whatsapp": validate_whatsapp_config(),
        "system": {
            "pythonpath": get_env_var("PYTHONPATH", "/app"),
            "timezone": get_env_var("TZ", "Asia/Jakarta"),
            "log_level": get_env_var("LOG_LEVEL", "INFO"),
        },
    }

    # Check overall validity
    for section in ["exchange", "openai", "telegram"]:
        if not results[section]["valid"]:
            results["overall_valid"] = False

    return results


def create_env_template(output_path: str = ".env.template") -> bool:
    """Create environment variables template"""
    try:
        template = """# Exchange Configuration
EXCHANGE=bybit
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
BYBIT_TESTNET=true

# Binance API (optional)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BINANCE_TESTNET=true

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_USER_ID=your_telegram_user_id_here

# WhatsApp (optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Other settings
PYTHONPATH=/app
TZ=Asia/Jakarta
LOG_LEVEL=INFO
"""

        with open(output_path, "w") as f:
            f.write(template)

        return True
    except Exception as e:
        print(f"Error creating env template: {e}")
        return False


def fix_env_issues() -> Dict[str, Any]:
    """Fix common environment variable issues - ENHANCED FOR DEPLOYMENT"""
    fixes_applied = []

    try:
        # Load .env file if it exists
        # env_vars = load_env_file(".env")  # Unused variable

        # Fix 1: Create .env template if .env doesn't exist
        if not Path(".env").exists():
            if create_env_template(".env"):
                fixes_applied.append("created_env_file")

        # Fix 2: Validate all environment variables
        validation_results = validate_all_env()

        if validation_results["overall_valid"]:
            fixes_applied.append("env_validation_passed")
        else:
            fixes_applied.append("env_validation_failed")

        # Fix 3: Set default values for missing optional variables - ENHANCED
        default_vars = {
            "PYTHONPATH": "/app",
            "TZ": "Asia/Jakarta",
            "LOG_LEVEL": "INFO",
            "EXCHANGE": "bybit",
            "BYBIT_TESTNET": "true",
            "BINANCE_TESTNET": "true",
            "SIMULATION_MODE": "false",
        }

        for key, default_value in default_vars.items():
            if not os.getenv(key):
                os.environ[key] = default_value
                fixes_applied.append(f"set_default_{key.lower()}")

        # Fix 4: Ensure critical paths exist
        critical_paths = ["logs", "data", "reports", "models"]
        for path in critical_paths:
            Path(path).mkdir(exist_ok=True)
            fixes_applied.append(f"created_dir_{path}")

        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "validation_results": validation_results,
        }

    except Exception as e:
        return {"success": False, "error": str(e), "fixes_applied": fixes_applied}


if __name__ == "__main__":
    # Run environment validation and fixes
    result = fix_env_issues()
    print(f"Environment fixes result: {result}")
