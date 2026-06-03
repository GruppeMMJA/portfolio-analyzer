"""
Portfolio persistence.
- Supabase (PostgreSQL) when configured  → multi-user, cloud-safe
- Local JSON fallback                    → local dev / no Supabase
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_BASE_DIR = Path.home() / ".portfolio_analyzer"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — decide which backend to use
# ─────────────────────────────────────────────────────────────────────────────

def _use_supabase(username: str) -> bool:
    from utils.supabase_client import is_configured
    return is_configured() and username not in ("local", "", None)


def _sb():
    from utils.supabase_client import get_client
    return get_client("service")


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio
# ─────────────────────────────────────────────────────────────────────────────

def save_portfolio(positions, username: str = "local") -> None:
    if _use_supabase(username):
        _sb_save_portfolio(positions, username)
    else:
        _json_save_portfolio(positions, username)


def load_portfolio(username: str = "local") -> Optional[list[dict]]:
    if _use_supabase(username):
        return _sb_load_portfolio(username)
    return _json_load_portfolio(username)


def delete_saved_portfolio(username: str = "local") -> None:
    if _use_supabase(username):
        _sb_delete_portfolio(username)
    else:
        _json_delete_portfolio(username)


def saved_portfolio_exists(username: str = "local") -> bool:
    if _use_supabase(username):
        data = _sb_load_portfolio(username)
        return bool(data)
    path = _json_path(username)
    return path.exists() and path.stat().st_size > 10


# ── Supabase backend ─────────────────────────────────────────────────────────

def _sb_save_portfolio(positions, user_id: str) -> None:
    client = _sb()
    if not client:
        return
    try:
        # Replace all existing rows for this user
        client.table("portfolios").delete().eq("user_id", user_id).execute()
        rows = [
            {
                "user_id":      user_id,
                "ticker":       p.ticker,
                "name":         p.name or "",
                "market_value": float(p.market_value),
                "currency":     getattr(p, "trade_currency", None) or getattr(p, "currency", "EUR"),
                "isin":         p.isin or "",
                "country":      p.country or "",
                "gics_sector":  int(p.gics_sector or 0),
                "asset_type":   p.asset_type.value if hasattr(p.asset_type, "value") else str(p.asset_type),
            }
            for p in positions
        ]
        if rows:
            client.table("portfolios").insert(rows).execute()
        logger.debug(f"Supabase: saved {len(rows)} positions for {user_id[:8]}")
    except Exception as e:
        logger.warning(f"Supabase save_portfolio failed ({e}), falling back to JSON")
        _json_save_portfolio(positions, user_id)


def _sb_load_portfolio(user_id: str) -> Optional[list[dict]]:
    client = _sb()
    if not client:
        return None
    try:
        resp = (
            client.table("portfolios")
            .select("ticker,name,market_value,currency,isin,country,gics_sector,asset_type")
            .eq("user_id", user_id)
            .execute()
        )
        data = resp.data or []
        return data if data else None
    except Exception as e:
        logger.warning(f"Supabase load_portfolio failed ({e}), falling back to JSON")
        return _json_load_portfolio(user_id)


def _sb_delete_portfolio(user_id: str) -> None:
    client = _sb()
    if not client:
        return
    try:
        client.table("portfolios").delete().eq("user_id", user_id).execute()
    except Exception as e:
        logger.warning(f"Supabase delete_portfolio failed: {e}")


# ── JSON backend (unchanged original logic) ───────────────────────────────────

def _json_path(username: str = "local") -> Path:
    safe = "".join(c for c in username if c.isalnum() or c in "-_")
    return _BASE_DIR / f"{safe}_portfolio.json"


def _json_save_portfolio(positions, username: str = "local") -> None:
    try:
        path = _json_path(username)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "ticker":       p.ticker,
                "name":         p.name or "",
                "market_value": p.market_value,
                "currency":     getattr(p, "trade_currency", None) or getattr(p, "currency", "EUR"),
                "isin":         p.isin or "",
                "country":      p.country or "",
                "gics_sector":  p.gics_sector or 0,
                "asset_type":   p.asset_type.value if hasattr(p.asset_type, "value") else str(p.asset_type),
            }
            for p in positions
        ]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"JSON save_portfolio failed: {e}")


def _json_load_portfolio(username: str = "local") -> Optional[list[dict]]:
    path = _json_path(username)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) and data else None
    except Exception as e:
        logger.warning(f"JSON load_portfolio failed: {e}")
        return None


def _json_delete_portfolio(username: str = "local") -> None:
    try:
        path = _json_path(username)
        if path.exists():
            path.unlink()
    except Exception as e:
        logger.warning(f"JSON delete_portfolio failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Profile (theme, avatar)
# ─────────────────────────────────────────────────────────────────────────────

def save_profile(username: str = "local", data: dict = None) -> None:
    if _use_supabase(username):
        _sb_save_profile(username, data or {})
    else:
        _json_save_profile(username, data or {})


def load_profile(username: str = "local") -> dict:
    if _use_supabase(username):
        return _sb_load_profile(username)
    return _json_load_profile(username)


# ── Supabase profile ──────────────────────────────────────────────────────────

def _sb_save_profile(user_id: str, data: dict) -> None:
    client = _sb()
    if not client:
        return
    try:
        row = {
            "user_id":    user_id,
            "theme":      data.get("theme", "midnight"),
            "avatar":     data.get("avatar", ""),
            "avatar_mime": data.get("avatar_mime", "image/jpeg"),
        }
        client.table("profiles").upsert(row, on_conflict="user_id").execute()
    except Exception as e:
        logger.warning(f"Supabase save_profile failed ({e}), falling back to JSON")
        _json_save_profile(user_id, data)


def _sb_load_profile(user_id: str) -> dict:
    client = _sb()
    if not client:
        return {}
    try:
        resp = (
            client.table("profiles")
            .select("theme,avatar,avatar_mime")
            .eq("user_id", user_id)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else {}
    except Exception as e:
        logger.warning(f"Supabase load_profile failed ({e}), falling back to JSON")
        return _json_load_profile(user_id)


# ── JSON profile ──────────────────────────────────────────────────────────────

def _json_profile_path(username: str = "local") -> Path:
    safe = "".join(c for c in username if c.isalnum() or c in "-_")
    return _BASE_DIR / f"{safe}_profile.json"


def _json_save_profile(username: str = "local", data: dict = None) -> None:
    try:
        path = _json_profile_path(username)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data or {}, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning(f"JSON save_profile failed: {e}")


def _json_load_profile(username: str = "local") -> dict:
    path = _json_profile_path(username)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"JSON load_profile failed: {e}")
        return {}
