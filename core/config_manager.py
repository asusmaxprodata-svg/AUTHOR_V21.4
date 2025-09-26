from .utils import load_json, save_json


def get_mode() -> str:
    state = load_json("data/state.json", {})
    return state.get("mode", "scalping")


def set_mode(mode: str):
    state = load_json("data/state.json", {})
    state["mode"] = mode
    save_json("data/state.json", state)


def get_leverage():
    state = load_json("data/state.json", {})
    return state.get("leverage", "auto")


def set_leverage(lev):
    state = load_json("data/state.json", {})
    state["leverage"] = lev
    save_json("data/state.json", state)


def set_testnet(flag: bool):
    state = load_json("data/state.json", {})
    state["testnet"] = bool(flag)
    save_json("data/state.json", state)


def get_symbol():
    g = load_json("config/global.json", {})
    return g.get("symbol", "BTCUSDT")


def set_symbol(sym: str):
    g = load_json("config/global.json", {})
    g["symbol"] = sym.upper()
    save_json("config/global.json", g)


def get_exchange() -> str:
    """Get current exchange with fallback"""
    try:
        g = load_json("config/global.json", {})
        return g.get("exchange", "bybit").lower()
    except Exception as e:
        print(f"Warning: Failed to get exchange config: {e}")
        return "bybit"


def set_exchange(name: str):
    """Set exchange with validation"""
    try:
        valid_exchanges = ["bybit", "binance"]
        if name.lower() not in valid_exchanges:
            raise ValueError(
                f"Invalid exchange: {name}. Must be one of {valid_exchanges}"
            )

        g = load_json("config/global.json", {})
        g["exchange"] = name.lower()
        save_json("config/global.json", g)
    except Exception as e:
        print(f"Error setting exchange: {e}")
        raise


def get_binance_testnet() -> bool:
    """Get Binance testnet setting from environment or config."""
    import os

    env_val = os.getenv("BINANCE_TESTNET", "").strip().lower()
    if env_val in ("true", "1", "yes", "on"):
        return True
    elif env_val in ("false", "0", "no", "off"):
        return False

    # Fallback to global config
    g = load_json("config/global.json", {})
    return bool(g.get("binance_testnet", True))


def set_binance_testnet(testnet: bool):
    """Set Binance testnet setting in global config."""
    g = load_json("config/global.json", {})
    g["binance_testnet"] = bool(testnet)
    save_json("config/global.json", g)


def get_exchange_config() -> dict:
    """Get exchange-specific configuration."""
    exchange = get_exchange()
    g = load_json("config/global.json", {})

    if exchange == "binance":
        return {
            "exchange": "binance",
            "testnet": get_binance_testnet(),
            "api_key": "BINANCE_API_KEY",
            "api_secret": "BINANCE_API_SECRET",
            "base_url": (
                "https://testnet.binancefuture.com"
                if get_binance_testnet()
                else "https://fapi.binance.com"
            ),
        }
    else:
        return {
            "exchange": "bybit",
            "testnet": bool(g.get("testnet", True)),
            "api_key": "BYBIT_API_KEY",
            "api_secret": "BYBIT_API_SECRET",
            "base_url": (
                "https://api-testnet.bybit.com"
                if bool(g.get("testnet", True))
                else "https://api.bybit.com"
            ),
        }


def get_watchlist():
    g = load_json("config/global.json", {})
    wl = g.get("symbols", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    return list(dict.fromkeys([s.upper() for s in wl]))


def add_watchlist(sym: str):
    g = load_json("config/global.json", {})
    wl = g.get("symbols", [])
    if sym.upper() not in wl:
        wl.append(sym.upper())
    g["symbols"] = wl
    save_json("config/global.json", g)


def remove_watchlist(sym: str):
    g = load_json("config/global.json", {})
    wl = [s for s in g.get("symbols", []) if s.upper() != sym.upper()]
    g["symbols"] = wl
    save_json("config/global.json", g)


def get_auto_pairs():
    g = load_json("config/global.json", {})
    return bool(g.get("auto_pairs", True))


def set_auto_pairs(flag: bool):
    g = load_json("config/global.json", {})
    g["auto_pairs"] = bool(flag)
    save_json("config/global.json", g)


def get_topn():
    g = load_json("config/global.json", {})
    return int(g.get("top_n", 3))


def set_topn(n: int):
    g = load_json("config/global.json", {})
    g["top_n"] = int(max(1, min(5, n)))
    save_json("config/global.json", g)


def get_pair_update_interval_min():
    g = load_json("config/global.json", {})
    return int(g.get("pair_update_interval_min", 15))


def set_pair_update_interval_min(m: int):
    g = load_json("config/global.json", {})
    m = int(max(1, min(180, int(m))))  # clamp to 1..180 minutes
    g["pair_update_interval_min"] = m
    save_json("config/global.json", g)


def get_leverage_caps():
    g = load_json("config/global.json", {})
    return g.get("leverage_caps", {"scalping": 50, "adaptive": 50})


def get_leverage_cap_for_mode(mode: str):
    caps = get_leverage_caps()
    return int(caps.get(mode, 50))


def clamp_leverage(mode: str, lev):
    try:
        cap = get_leverage_cap_for_mode(mode)
    except Exception:
        cap = 50
    if isinstance(lev, (int, float)):
        lev = int(max(1, min(cap, int(lev))))
        return lev
    # string ("auto") passes through; enforcement happens when resolved
    return lev


def get_running():
    g = load_json("config/global.json", {})
    return bool(g.get("running", True))


def set_running(flag: bool):
    g = load_json("config/global.json", {})
    g["running"] = bool(flag)
    save_json("config/global.json", g)
