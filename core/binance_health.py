# core/binance_health.py
"""
Binance-specific health check functions
"""
import os
import time
from typing import Dict, Any
from .binance_client import get_binance_client
from .logger import get_logger

log = get_logger("binance_health")


def check_binance_connection(testnet: bool = True) -> Dict[str, Any]:
    """Check Binance API connection"""
    try:
        client = get_binance_client(testnet=testnet)
        if not client:
            return {
                "status": "error",
                "message": (
                    "Binance client not initialized - missing API credentials"
                ),
                "details": {
                    "api_key_present": bool(os.getenv("BINANCE_API_KEY")),
                    "api_secret_present": bool(
                        os.getenv("BINANCE_API_SECRET")
                    ),
                    "testnet": testnet,
                },
            }

        # Test connection
        if client.test_connection():
            return {
                "status": "healthy",
                "message": f'Binance {("testnet" if testnet else "mainnet")} '
                f'connection successful',
                "details": {"testnet": testnet, "exchange": "binance"},
            }
        else:
            return {
                "status": "error",
                "message": f'Binance {("testnet" if testnet else "mainnet")} '
                f'connection failed',
                "details": {"testnet": testnet, "exchange": "binance"},
            }

    except Exception as e:
        log.error(f"Binance health check error: {e}")
        return {
            "status": "error",
            "message": f"Binance health check failed: {str(e)}",
            "details": {
                "testnet": testnet, "exchange": "binance", "error": str(e)
            },
        }


def check_binance_balance(testnet: bool = True) -> Dict[str, Any]:
    """Check Binance account balance"""
    try:
        client = get_binance_client(testnet=testnet)
        if not client:
            return {
                "status": "error",
                "message": "Binance client not available",
                "details": {},
            }

        balance = client.get_account_balance()
        if not balance:
            return {
                "status": "error",
                "message": "Failed to fetch Binance balance",
                "details": {},
            }

        # Check if we have USDT balance
        usdt_balance = balance.get("total", {}).get("USDT", 0)
        free_usdt = balance.get("free", {}).get("USDT", 0)

        return {
            "status": "healthy" if usdt_balance > 0 else "warning",
            "message": (
                f"Binance balance: {usdt_balance:.4f} USDT "
                f"(free: {free_usdt:.4f})"
            ),
            "details": {
                "total_usdt": float(usdt_balance),
                "free_usdt": float(free_usdt),
                "testnet": testnet,
            },
        }

    except Exception as e:
        log.error(f"Binance balance check error: {e}")
        return {
            "status": "error",
            "message": f"Binance balance check failed: {str(e)}",
            "details": {"testnet": testnet, "error": str(e)},
        }


def check_binance_positions(testnet: bool = True) -> Dict[str, Any]:
    """Check Binance open positions"""
    try:
        client = get_binance_client(testnet=testnet)
        if not client:
            return {
                "status": "error",
                "message": "Binance client not available",
                "details": {},
            }

        positions = client.get_positions()
        open_positions = [p for p in positions if float(p.get("size", 0)) > 0]

        return {
            "status": "healthy",
            "message": f"Binance positions: {len(open_positions)} open",
            "details": {
                "total_positions": len(positions),
                "open_positions": len(open_positions),
                "positions": open_positions[:5],  # Limit to first 5
                "testnet": testnet,
            },
        }

    except Exception as e:
        log.error(f"Binance positions check error: {e}")
        return {
            "status": "error",
            "message": f"Binance positions check failed: {str(e)}",
            "details": {"testnet": testnet, "error": str(e)},
        }


def check_binance_market_data(
    symbol: str = "BTCUSDT", testnet: bool = True
) -> Dict[str, Any]:
    """Check Binance market data availability"""
    try:
        client = get_binance_client(testnet=testnet)
        if not client:
            return {
                "status": "error",
                "message": "Binance client not available",
                "details": {},
            }

        # Test ticker
        ticker = client.get_ticker(symbol)
        if not ticker or not ticker.get("last"):
            return {
                "status": "error",
                "message": f"Failed to fetch {symbol} ticker from Binance",
                "details": {"symbol": symbol, "testnet": testnet},
            }

        # Test klines
        klines = client.get_klines(symbol, "5m", 10)
        if klines.empty:
            return {
                "status": "error",
                "message": f"Failed to fetch {symbol} klines from Binance",
                "details": {"symbol": symbol, "testnet": testnet},
            }

        return {
            "status": "healthy",
            "message": f"Binance market data for {symbol} available",
            "details": {
                "symbol": symbol,
                "last_price": float(ticker.get("last", 0)),
                "klines_count": len(klines),
                "testnet": testnet,
            },
        }

    except Exception as e:
        log.error(f"Binance market data check error: {e}")
        return {
            "status": "error",
            "message": f"Binance market data check failed: {str(e)}",
            "details": {"symbol": symbol, "testnet": testnet, "error": str(e)},
        }


def get_binance_health_summary(testnet: bool = True) -> Dict[str, Any]:
    """Get comprehensive Binance health summary"""
    checks = {
        "connection": check_binance_connection(testnet),
        "balance": check_binance_balance(testnet),
        "positions": check_binance_positions(testnet),
        "market_data": check_binance_market_data("BTCUSDT", testnet),
    }

    # Determine overall status
    statuses = [check.get("status", "unknown") for check in checks.values()]
    if "error" in statuses:
        overall_status = "error"
    elif "warning" in statuses:
        overall_status = "warning"
    else:
        overall_status = "healthy"

    return {
        "overall_status": overall_status,
        "exchange": "binance",
        "testnet": testnet,
        "timestamp": time.time(),
        "checks": checks,
    }
