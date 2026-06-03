"""
Supabase client singleton.
Returns None when Supabase is not configured (local dev mode).
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Module-level cache — one client per role per process
_clients: dict = {}


def is_configured() -> bool:
    """True when secrets.toml contains a [supabase] section."""
    try:
        return "supabase" in st.secrets
    except Exception:
        return False


def get_client(role: str = "anon"):
    """
    Return a Supabase client or None if not configured.

    role="anon"    — uses the anon key   (safe for auth operations)
    role="service" — uses service_role key (server-side DB operations only)
    """
    if not is_configured():
        return None

    if role in _clients:
        return _clients[role]

    try:
        from supabase import create_client

        url = st.secrets["supabase"]["url"]
        if role == "service":
            key = st.secrets["supabase"].get(
                "service_role_key",
                st.secrets["supabase"]["anon_key"],
            )
        else:
            key = st.secrets["supabase"]["anon_key"]

        client = create_client(url, key)
        _clients[role] = client
        logger.debug(f"Supabase client created (role={role})")
        return client

    except Exception as e:
        logger.error(f"Supabase client init failed: {e}")
        return None
