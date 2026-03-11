"""Temporary debug panel — remove after fixing Volume path."""
import os
import streamlit as st


def render_debug():
    st.markdown("### 🔍 Volume Path Diagnostics")
    
    volume_path = os.environ.get("CONTRACTS_VOLUME_PATH", "NOT SET")
    st.code(f"CONTRACTS_VOLUME_PATH = {volume_path}")
    
    # Check what /Volumes looks like from inside the container
    st.markdown("**Contents of `/Volumes`:**")
    try:
        entries = os.listdir("/Volumes")
        st.code("\n".join(entries) if entries else "(empty)")
    except Exception as e:
        st.error(f"/Volumes: {e}")

    # Walk down the path step by step
    st.markdown("**Path existence check:**")
    parts = [
        "/Volumes",
        "/Volumes/uc_demos_giovanny_lasso",
        "/Volumes/uc_demos_giovanny_lasso/performance_optimization",
        "/Volumes/uc_demos_giovanny_lasso/performance_optimization/data_contracts",
    ]
    rows = ""
    for p in parts:
        exists = os.path.exists(p)
        if exists:
            try:
                contents = os.listdir(p)
                info = f"✅ exists — {len(contents)} items inside"
            except Exception as e:
                info = f"✅ exists but cannot list: {e}"
        else:
            info = "❌ NOT FOUND"
        rows += f"- `{p}` → {info}\n"
    st.markdown(rows)

    # Try a write test
    st.markdown("**Write test:**")
    test_path = os.path.join(volume_path, "_write_test.tmp")
    try:
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        st.success(f"✅ Write OK to `{volume_path}`")
    except Exception as e:
        st.error(f"❌ Write failed: {type(e).__name__}: {e}")

    # Show env vars
    st.markdown("**Relevant env vars:**")
    env_keys = [k for k in os.environ if "VOLUME" in k or "DATABRICKS" in k or "PATH" in k.upper()]
    for k in sorted(env_keys):
        st.code(f"{k} = {os.environ[k]}")
