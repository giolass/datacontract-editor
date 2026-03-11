"""
Persistence layer — Databricks Files API (OAuth M2M).

/Volumes is NOT mounted in Databricks Apps containers.
Files must be read/written via the Databricks Files API using OAuth credentials
that are automatically injected by the Apps runtime:
  - DATABRICKS_HOST
  - DATABRICKS_CLIENT_ID
  - DATABRICKS_CLIENT_SECRET
"""
import os
import requests
import streamlit as st
from typing import List, Optional

# ── Configuration ─────────────────────────────────────────────────────────────
VOLUME_PATH = os.environ.get(
    "CONTRACTS_VOLUME_PATH",
    os.path.join(os.path.dirname(__file__), "..", "local_contracts"),
).rstrip("/")

_IS_DATABRICKS = VOLUME_PATH.startswith("/Volumes/")

_HOST          = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
_CLIENT_ID     = os.environ.get("DATABRICKS_CLIENT_ID", "")
_CLIENT_SECRET = os.environ.get("DATABRICKS_CLIENT_SECRET", "")

_USE_API = _IS_DATABRICKS and bool(_HOST) and bool(_CLIENT_ID) and bool(_CLIENT_SECRET)

# ── OAuth token (cached in session) ──────────────────────────────────────────

def _get_token() -> str:
    """Get OAuth access token using client credentials (M2M)."""
    if "dbx_access_token" in st.session_state:
        return st.session_state["dbx_access_token"]

    # Extract workspace ID from host: adb-<id>.azuredatabricks.net
    token_url = f"{_HOST}/oidc/v1/token"
    try:
        r = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "scope": "all-apis",
            },
            auth=(_CLIENT_ID, _CLIENT_SECRET),
            timeout=10,
        )
        if r.status_code == 200:
            token = r.json()["access_token"]
            st.session_state["dbx_access_token"] = token
            return token
        else:
            st.error(f"OAuth token error {r.status_code}: {r.text[:200]}")
            return ""
    except Exception as e:
        st.error(f"OAuth token request failed: {e}")
        return ""


def _headers() -> dict:
    token = _get_token()
    return {"Authorization": f"Bearer {token}"}


# ── Public API ────────────────────────────────────────────────────────────────

def list_contracts() -> List[str]:
    return _api_list() if _USE_API else _local_list()


def load_contract(filename: str) -> Optional[str]:
    return _api_load(filename) if _USE_API else _local_load(filename)


def save_contract(filename: str, yaml_content: str) -> bool:
    if not filename.endswith((".yaml", ".yml")):
        filename += ".yaml"
    return _api_save(filename, yaml_content) if _USE_API else _local_save(filename, yaml_content)


def delete_contract(filename: str) -> bool:
    return _api_delete(filename) if _USE_API else _local_delete(filename)


# ── Databricks Files API ──────────────────────────────────────────────────────

def _api_list() -> List[str]:
    url = f"{_HOST}/api/2.0/fs/directories{VOLUME_PATH}"
    try:
        r = requests.get(url, headers=_headers(), timeout=10)
        if r.status_code == 200:
            contents = r.json().get("contents", [])
            return sorted([
                item["name"] for item in contents
                if not item.get("is_directory", False)
                and item["name"].endswith((".yaml", ".yml"))
            ])
        elif r.status_code == 401:
            # Token expired — clear cache and retry once
            st.session_state.pop("dbx_access_token", None)
            r2 = requests.get(url, headers=_headers(), timeout=10)
            if r2.status_code == 200:
                contents = r2.json().get("contents", [])
                return sorted([
                    item["name"] for item in contents
                    if not item.get("is_directory", False)
                    and item["name"].endswith((".yaml", ".yml"))
                ])
        st.error(f"Files API list error {r.status_code}: {r.text[:200]}")
        return []
    except Exception as e:
        st.error(f"Files API list failed: {e}")
        return []


def _api_load(filename: str) -> Optional[str]:
    url = f"{_HOST}/api/2.0/fs/files{VOLUME_PATH}/{filename}"
    try:
        r = requests.get(url, headers=_headers(), timeout=10)
        if r.status_code == 200:
            return r.text
        st.error(f"Cannot load '{filename}': {r.status_code} {r.text[:200]}")
        return None
    except Exception as e:
        st.error(f"Files API load failed: {e}")
        return None


def _api_save(filename: str, yaml_content: str) -> bool:
    url = f"{_HOST}/api/2.0/fs/files{VOLUME_PATH}/{filename}"
    try:
        r = requests.put(
            url,
            headers={
                "Authorization": f"Bearer {_get_token()}",
                "Content-Type": "application/octet-stream",
            },
            data=yaml_content.encode("utf-8"),
            params={"overwrite": "true"},
            timeout=15,
        )
        if r.status_code in (200, 201, 204):
            return True
        st.error(f"Cannot save '{filename}': {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        st.error(f"Files API save failed: {e}")
        return False


def _api_delete(filename: str) -> bool:
    url = f"{_HOST}/api/2.0/fs/files{VOLUME_PATH}/{filename}"
    try:
        r = requests.delete(url, headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        st.error(f"Files API delete failed: {e}")
        return False


# ── Local filesystem fallback (dev/local only) ────────────────────────────────

def _local_list() -> List[str]:
    os.makedirs(VOLUME_PATH, exist_ok=True)
    try:
        return sorted([f for f in os.listdir(VOLUME_PATH) if f.endswith((".yaml", ".yml"))])
    except Exception as e:
        st.error(f"Cannot list contracts: {e}")
        return []


def _local_load(filename: str) -> Optional[str]:
    try:
        with open(os.path.join(VOLUME_PATH, filename), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Cannot load '{filename}': {e}")
        return None


def _local_save(filename: str, yaml_content: str) -> bool:
    os.makedirs(VOLUME_PATH, exist_ok=True)
    try:
        with open(os.path.join(VOLUME_PATH, filename), "w", encoding="utf-8") as f:
            f.write(yaml_content)
        return True
    except Exception as e:
        st.error(f"Cannot save '{filename}': {e}")
        return False


def _local_delete(filename: str) -> bool:
    try:
        os.remove(os.path.join(VOLUME_PATH, filename))
        return True
    except Exception as e:
        st.error(f"Cannot delete '{filename}': {e}")
        return False
