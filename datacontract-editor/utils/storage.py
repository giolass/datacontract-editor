"""
Persistence layer — Databricks Volumes (YAML files).
Falls back to local filesystem when running outside Databricks.

IMPORTANT for Databricks Apps:
  - /Volumes/... paths already exist as Unity Catalog mount points.
  - NEVER call makedirs() on a /Volumes path — raises PermissionError.
  - The Volume must be pre-created in Unity Catalog BEFORE deploying:
      CREATE VOLUME <catalog>.<schema>.<volume_name>;
  - Set env var CONTRACTS_VOLUME_PATH=/Volumes/catalog/schema/volume in app.yaml.
"""
import os
import streamlit as st
from typing import List, Optional

# ── Configuration ─────────────────────────────────────────────────────────────
VOLUME_PATH = os.environ.get(
    "CONTRACTS_VOLUME_PATH",
    os.path.join(os.path.dirname(__file__), "..", "local_contracts"),
)

# Databricks Volume paths start with /Volumes/ — they must NOT be created
# with makedirs; they are managed by Unity Catalog.
_IS_DATABRICKS_VOLUME = VOLUME_PATH.startswith("/Volumes/")


def _ensure_dir():
    """
    Only create directories for LOCAL (non-Volume) paths.
    For Databricks Volumes, the directory must already exist in Unity Catalog.
    """
    if not _IS_DATABRICKS_VOLUME:
        os.makedirs(VOLUME_PATH, exist_ok=True)


def list_contracts() -> List[str]:
    """Return filenames of all saved YAML contracts."""
    _ensure_dir()
    try:
        files = [f for f in os.listdir(VOLUME_PATH) if f.endswith((".yaml", ".yml"))]
        return sorted(files)
    except FileNotFoundError:
        if _IS_DATABRICKS_VOLUME:
            # Extract catalog.schema.volume from /Volumes/catalog/schema/volume
            uc_path = VOLUME_PATH.replace("/Volumes/", "").replace("/", ".", 2)
            st.error(
                f"⚠️ Volume not found: `{VOLUME_PATH}`\n\n"
                f"Create it first in Databricks SQL:\n"
                f"`CREATE VOLUME {uc_path};`"
            )
        else:
            os.makedirs(VOLUME_PATH, exist_ok=True)
        return []
    except PermissionError:
        st.error(
            f"⚠️ Permission denied on `{VOLUME_PATH}`.\n\n"
            f"Grant the app's service principal **READ VOLUME** and **WRITE VOLUME** "
            f"privileges in Unity Catalog → Data → Volumes."
        )
        return []
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
    except PermissionError:
        st.error(
            f"⚠️ Permission denied writing to `{VOLUME_PATH}`.\n\n"
            f"Grant **WRITE VOLUME** privilege on this Volume in Unity Catalog."
        )
        return False
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
