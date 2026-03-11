"""
Persistence layer — Databricks Volumes (YAML files).
Falls back to local filesystem when running outside Databricks.
"""
import os
import streamlit as st
from typing import List, Optional

# ── Configuration ────────────────────────────────────────────────────────────
# In Databricks Apps, set CONTRACTS_VOLUME_PATH as an env variable, e.g.:
#   /Volumes/main/default/data_contracts
# Outside Databricks, defaults to ./local_contracts/
VOLUME_PATH = os.environ.get(
    "CONTRACTS_VOLUME_PATH",
    os.path.join(os.path.dirname(__file__), "..", "local_contracts"),
)


def _ensure_dir():
    os.makedirs(VOLUME_PATH, exist_ok=True)


def list_contracts() -> List[str]:
    """Return filenames of all saved YAML contracts."""
    _ensure_dir()
    try:
        files = [f for f in os.listdir(VOLUME_PATH) if f.endswith((".yaml", ".yml"))]
        return sorted(files)
    except Exception as e:
        st.error(f"Cannot list contracts: {e}")
        return []


def load_contract(filename: str) -> Optional[str]:
    """Load YAML content from Volume."""
    path = os.path.join(VOLUME_PATH, filename)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as e:
        st.error(f"Cannot load '{filename}': {e}")
        return None


def save_contract(filename: str, yaml_content: str) -> bool:
    """Save YAML content to Volume. Returns True on success."""
    _ensure_dir()
    if not filename.endswith((".yaml", ".yml")):
        filename += ".yaml"
    path = os.path.join(VOLUME_PATH, filename)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(yaml_content)
        return True
    except Exception as e:
        st.error(f"Cannot save '{filename}': {e}")
        return False


def delete_contract(filename: str) -> bool:
    """Delete a contract file from Volume."""
    path = os.path.join(VOLUME_PATH, filename)
    try:
        os.remove(path)
        return True
    except Exception as e:
        st.error(f"Cannot delete '{filename}': {e}")
        return False
