# core/ai_signal.py — Minimal LLM integration for kang_bot
import os
import time
import json
import pathlib
import logging
from core.utils import load_json
from typing import Dict, Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # fallback if sdk not installed

CACHE_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "llm_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _logger():
    try:
        from core.logger import get_logger

        return get_logger("ai_signal")
    except Exception:
        return logging.getLogger("ai_signal")


log = _logger()


def _load_cfg():
    try:
        from core.config_manager import load_config

        cfg = load_config()
        return cfg.get("llm", {}) if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def _client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or OpenAI is None:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        log.warning(f"OpenAI init failed: {e}")
        return None


def _cache_get(kind: str, key: str, max_age_sec: int):
    p = CACHE_DIR / f"{kind}_{key}.json"
    if not p.exists():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if time.time() - obj.get("_ts", 0) <= max_age_sec:
            return obj.get("data")
    except Exception:
        return None
    return None


def _cache_set(kind: str, key: str, data: Any):
    p = CACHE_DIR / f"{kind}_{key}.json"
    p.write_text(
        json.dumps({"_ts": time.time(), "data": data}), encoding="utf-8"
    )


def _call_llm_json(
    prompt: str, max_tokens: int = None, timeout_s: float = None
) -> Dict[str, Any]:
    """Call OpenAI API with robust error handling and fallbacks"""
    cli = _client()
    if cli is None:
        return {"error": "OpenAI client not available", "bias": 0.5}

    # Load configurable constants
    try:
        constants = load_json("config/constants.json", {})
        openai_config = constants.get("openai", {})
        max_tokens = max_tokens or openai_config.get(
            "default_max_tokens", 200
        )
        timeout_s = timeout_s or openai_config.get("default_timeout", 0.6)
        default_model = openai_config.get("default_model", "gpt-4o-mini")
    except Exception:
        max_tokens = max_tokens or 200
        timeout_s = timeout_s or 0.6
        default_model = "gpt-4o-mini"

    model = (os.getenv("OPENAI_MODEL_MINI") or 
             os.getenv("OPENAI_MODEL") or default_model)
    try:
        resp = cli.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return ONLY valid JSON. Keys must be simple.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            timeout=timeout_s,
        )
        content = resp.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except Exception:
            content = content.strip()
            if content.startswith("```"):
                if "\n" in content:
                    content = content.strip("`").split("\n", 1)[1]
                else:
                    content = "{}"
            try:
                return json.loads(content)
            except Exception:
                # Final fallback: return safe default
                return {"error": "Invalid JSON response", "bias": 0.5}
    except Exception as e:
        log = _logger()
        log.warning(f"LLM call failed: {e}")
        # Return safe fallback instead of empty dict
        return {"error": str(e), "bias": 0.5}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def llm_pair_score(symbol: str, snapshot: Dict[str, Any]) -> float:
    key = f"pair_{symbol}"
    cached = _cache_get("pair", key, max_age_sec=30 * 60)
    if cached is not None:
        return float(cached)
    snap = {
        k: float(snapshot.get(k, 0) or 0)
        for k in ("ret24h", "atr", "eff", "spread_bps", "funding")
    }
    prompt = (
        'You are a quant co-pilot. Given numeric snapshot, '
        'output JSON {"score": -1..1}.\n'
        f"symbol={symbol}\n"
        f"{json.dumps(snap)}\n"
        "Rules: prefer higher score for clean trends, healthy volatility, "
        "reasonable spread; lower score for choppy/whipsaw/noisy conditions. "
        "No text, JSON only."
    )
    obj = _call_llm_json(
        prompt,
        max_tokens=60,
        timeout_s=float(_load_cfg().get("timeout_ms", 600)) / 1000.0 or 0.6,
    )
    score = float(obj.get("score", 0.0) if isinstance(obj, dict) else 0.0)
    score = _clamp(score, -1.0, 1.0)
    _cache_set("pair", key, score)
    return score


def llm_context_score(symbol: str, snapshot: Dict[str, Any]) -> float:
    key = f"context_{symbol}"
    cached = _cache_get("context", key, max_age_sec=30 * 60)
    if cached is not None:
        return float(cached)
    snap = {
        k: float(snapshot.get(k, 0) or 0)
        for k in ("ret1h", "ret4h", "atr", "eff", "volatility", "spread_bps")
    }
    prompt = (
        'Output JSON {"ctx": -1..1} summarizing if context '
        'favors directional entries.\n'
        f"symbol={symbol}\n"
        f"{json.dumps(snap)}\n"
        "No explanations. JSON only."
    )
    obj = _call_llm_json(
        prompt,
        max_tokens=60,
        timeout_s=float(_load_cfg().get("timeout_ms", 600)) / 1000.0 or 0.6,
    )
    ctx = float(obj.get("ctx", 0.0) if isinstance(obj, dict) else 0.0)
    ctx = _clamp(ctx, -1.0, 1.0)
    _cache_set("context", key, ctx)
    return ctx


def llm_confirm(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = (
        'Return JSON {"ok": true|false, "why": "..."}. '
        'Approve only if conditions are reasonable.\n'
        f"{json.dumps(payload)}\n"
        "No extra text."
    )
    obj = _call_llm_json(
        prompt,
        max_tokens=80,
        timeout_s=float(_load_cfg().get("timeout_ms", 600)) / 1000.0 or 0.6,
    )
    if not obj:
        return {"ok": True, "why": "fallback"}
    ok = bool(obj.get("ok", True))
    why = str(obj.get("why", ""))
    return {"ok": ok, "why": why}
