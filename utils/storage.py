"""
Persistence — Databricks Files API (OAuth M2M).
Volume path is determined at runtime from session state (user-defined)
with fallback to CONTRACTS_VOLUME_PATH env var.
"""
import os, requests, streamlit as st
from typing import List, Optional

# ── Host + credentials (injected by Databricks Apps runtime) ──────────────────
_raw_host      = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
_HOST          = _raw_host if _raw_host.startswith("http") else f"https://{_raw_host}"
_CLIENT_ID     = os.environ.get("DATABRICKS_CLIENT_ID", "")
_CLIENT_SECRET = os.environ.get("DATABRICKS_CLIENT_SECRET", "")

# ── Env-level fallback volume path ────────────────────────────────────────────
_ENV_VOLUME_PATH = os.environ.get(
    "CONTRACTS_VOLUME_PATH",
    os.path.join(os.path.dirname(__file__), "..", "local_contracts"),
).rstrip("/")

_IS_DATABRICKS = _HOST not in ("", "https://") and bool(_CLIENT_ID)


def _get_volume_path() -> str:
    """
    Priority:
      1. Session state save params (user-defined via UI)
      2. CONTRACTS_VOLUME_PATH env var
      3. local_contracts folder (dev fallback)
    """
    cat = st.session_state.get("save_catalog", "").strip()
    sch = st.session_state.get("save_schema",  "").strip()
    vol = st.session_state.get("save_volume",  "").strip()
    if cat and sch and vol:
        return f"/Volumes/{cat}/{sch}/{vol}"
    return _ENV_VOLUME_PATH


def _use_api() -> bool:
    return _get_volume_path().startswith("/Volumes/") and _IS_DATABRICKS


# ── OAuth token ───────────────────────────────────────────────────────────────
def _get_token() -> str:
    if "dbx_access_token" in st.session_state:
        return st.session_state["dbx_access_token"]
    try:
        r = requests.post(
            f"{_HOST}/oidc/v1/token",
            data={"grant_type": "client_credentials", "scope": "all-apis"},
            auth=(_CLIENT_ID, _CLIENT_SECRET), timeout=10,
        )
        if r.status_code == 200:
            token = r.json()["access_token"]
            st.session_state["dbx_access_token"] = token
            return token
        st.error(f"OAuth error {r.status_code}: {r.text[:200]}")
        return ""
    except Exception as e:
        st.error(f"OAuth failed: {e}")
        return ""


def _headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}"}


# ── Public API ────────────────────────────────────────────────────────────────
def list_contracts() -> List[str]:
    return _api_list() if _use_api() else _local_list()

def load_contract(filename: str) -> Optional[str]:
    return _api_load(filename) if _use_api() else _local_load(filename)

def save_contract(filename: str, yaml_content: str, volume_path: str = None) -> bool:
    if not filename.endswith((".yaml", ".yml")):
        filename += ".yaml"
    path = volume_path or _get_volume_path()
    if path.startswith("/Volumes/") and _IS_DATABRICKS:
        return _api_save(filename, yaml_content, path)
    return _local_save(filename, yaml_content)

def delete_contract(filename: str) -> bool:
    return _api_delete(filename) if _use_api() else _local_delete(filename)

def get_current_volume_path() -> str:
    return _get_volume_path()


# ── Databricks Files API ──────────────────────────────────────────────────────
def _api_list() -> List[str]:
    path = _get_volume_path()
    url  = f"{_HOST}/api/2.0/fs/directories{path}"
    try:
        r = requests.get(url, headers=_headers(), timeout=10)
        if r.status_code == 401:
            st.session_state.pop("dbx_access_token", None)
            r = requests.get(url, headers=_headers(), timeout=10)
        if r.status_code == 200:
            return sorted([
                i["name"] for i in r.json().get("contents", [])
                if not i.get("is_directory") and i["name"].endswith((".yaml",".yml"))
            ])
        return []
    except Exception:
        return []

def _api_load(filename: str) -> Optional[str]:
    path = _get_volume_path()
    url  = f"{_HOST}/api/2.0/fs/files{path}/{filename}"
    try:
        r = requests.get(url, headers=_headers(), timeout=10)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None

def _api_save(filename: str, yaml_content: str, path: str) -> bool:
    url = f"{_HOST}/api/2.0/fs/files{path}/{filename}"
    try:
        r = requests.put(
            url,
            headers={"Authorization": f"Bearer {_get_token()}", "Content-Type": "application/octet-stream"},
            data=yaml_content.encode("utf-8"),
            params={"overwrite": "true"}, timeout=15,
        )
        return r.status_code in (200, 201, 204)
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False

def _api_delete(filename: str) -> bool:
    path = _get_volume_path()
    url  = f"{_HOST}/api/2.0/fs/files{path}/{filename}"
    try:
        r = requests.delete(url, headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False


# ── Local fallback ────────────────────────────────────────────────────────────
def _local_list() -> List[str]:
    p = _get_volume_path()
    os.makedirs(p, exist_ok=True)
    try:
        return sorted([f for f in os.listdir(p) if f.endswith((".yaml",".yml"))])
    except Exception:
        return []

def _local_load(filename: str) -> Optional[str]:
    try:
        with open(os.path.join(_get_volume_path(), filename), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def _local_save(filename: str, yaml_content: str) -> bool:
    p = _get_volume_path()
    os.makedirs(p, exist_ok=True)
    try:
        with open(os.path.join(p, filename), "w", encoding="utf-8") as f:
            f.write(yaml_content)
        return True
    except Exception as e:
        st.error(f"Local save failed: {e}")
        return False

def _local_delete(filename: str) -> bool:
    try:
        os.remove(os.path.join(_get_volume_path(), filename))
        return True
    except Exception:
        return False
