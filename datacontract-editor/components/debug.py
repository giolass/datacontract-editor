"""Diagnostics panel — OAuth token + Files API test."""
import os
import requests
import streamlit as st


def render_debug():
    st.markdown("### 🔍 Storage Diagnostics")

    tmp_h = os.environ.get("DATABRICKS_HOST", "❌ NOT SET").rstrip("/")
    host   = tmp_h if tmp_h.startswith("http") else f"https://{tmp_h}"
    cid    = os.environ.get("DATABRICKS_CLIENT_ID", "❌ NOT SET")
    secret = os.environ.get("DATABRICKS_CLIENT_SECRET", "")
    vpath  = os.environ.get("CONTRACTS_VOLUME_PATH", "❌ NOT SET")

    st.markdown("#### Environment")
    st.code(
        f"DATABRICKS_HOST          = {host}\n"
        f"DATABRICKS_CLIENT_ID     = {cid}\n"
        f"DATABRICKS_CLIENT_SECRET = {'✅ SET (' + str(len(secret)) + ' chars)' if secret else '❌ NOT SET'}\n"
        f"CONTRACTS_VOLUME_PATH    = {vpath}"
    )

    # Step 1: get token
    st.markdown("#### Step 1 — OAuth Token")
    token = ""
    if host == "❌ NOT SET" or not secret:
        st.error("Missing DATABRICKS_HOST or DATABRICKS_CLIENT_SECRET")
    else:
        try:
            r = requests.post(
                f"{host}/oidc/v1/token",
                data={"grant_type": "client_credentials", "scope": "all-apis"},
                auth=(cid, secret),
                timeout=10,
            )
            if r.status_code == 200:
                token = r.json()["access_token"]
                st.success(f"✅ OAuth token obtained ({len(token)} chars)")
            else:
                st.error(f"❌ Token error {r.status_code}: {r.text[:300]}")
        except Exception as e:
            st.error(f"❌ Token request failed: {e}")

    # Step 2: list Volume via Files API
    st.markdown("#### Step 2 — Files API (list Volume)")
    if token and vpath != "❌ NOT SET":
        url = f"{host}/api/2.0/fs/directories{vpath}"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if r.status_code == 200:
                items = r.json().get("contents", [])
                st.success(f"✅ Files API OK — {len(items)} files in Volume")
                if items:
                    for item in items[:10]:
                        st.write(f"  - {item['name']}")
            else:
                st.error(f"❌ Files API {r.status_code}: {r.text[:300]}")
        except Exception as e:
            st.error(f"❌ Files API failed: {e}")

    # Step 3: write test via API
    st.markdown("#### Step 3 — Write Test via Files API")
    if token and vpath != "❌ NOT SET":
        test_url = f"{host}/api/2.0/fs/files{vpath}/_write_test.tmp"
        try:
            r = requests.put(
                test_url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
                data=b"ok",
                params={"overwrite": "true"},
                timeout=10,
            )
            if r.status_code in (200, 201, 204):
                # cleanup
                requests.delete(test_url, headers={"Authorization": f"Bearer {token}"})
                st.success("✅ Write via Files API works!")
            else:
                st.error(f"❌ Write failed {r.status_code}: {r.text[:300]}")
        except Exception as e:
            st.error(f"❌ Write test failed: {e}")
