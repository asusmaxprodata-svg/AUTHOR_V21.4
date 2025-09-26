import requests
import time
from typing import Dict, Any
from .config_manager import get_exchange

try:
    from core.ai_signal import (
        llm_context_score  # optional import used by helper
    )
except Exception:
    llm_context_score = None  # type: ignore


def bybit_base(testnet: bool) -> str:
    return (
        "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
    )


def get_orderbook(
    symbol: str,
    testnet: bool = True,
    category: str = "linear",
    limit: int = 50,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetch orderbook snapshot from Bybit v5 REST.
    Returns dict with 'bids'/'asks' lists of [price(size as float)].
    """
    ex = get_exchange()
    if ex == "binance":
        try:
            # Binance Futures (USDⓈ-M) depth endpoint
            base = (
                "https://testnet.binancefuture.com"
                if bool(testnet)
                else "https://fapi.binance.com"
            )
            resp = requests.get(
                f"{base}/fapi/v1/depth",
                params={"symbol": symbol, "limit": min(limit, 1000)},
                timeout=timeout,
            )
            resp.raise_for_status()
            j = resp.json()
            bids = [(float(p), float(s)) for p, s in j.get("bids", []) if float(s) > 0]
            asks = [(float(p), float(s)) for p, s in j.get("asks", []) if float(s) > 0]
            return {"bids": bids, "asks": asks, "ts": int(time.time() * 1000)}
        except Exception as e:
            # Fallback to empty result with reason
            return {
                "bids": [],
                "asks": [],
                "ts": None,
                "error": f"binance_depth_failed: {e}",
            }
    # default: bybit
    url = f"{bybit_base(testnet)}/v5/market/orderbook"
    params = {"category": category, "symbol": symbol, "limit": limit}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    j = r.json()
    if j.get("retCode") != 0:
        raise RuntimeError(f"Bybit error: {j.get('retMsg')} ({j.get('retCode')})")
    res = j["result"]
    bids = [(float(p), float(s)) for p, s in res.get("b", []) if float(s) > 0]
    asks = [(float(p), float(s)) for p, s in res.get("a", []) if float(s) > 0]
    return {"bids": bids, "asks": asks, "ts": res.get("ts")}


# Optional: LLM context feature (fallback 0.0 if fails)
def _llm_context_feature(symbol: str, snapshot: dict) -> float:
    try:
        return float(llm_context_score(symbol, snapshot))
    except Exception:
        return 0.0
