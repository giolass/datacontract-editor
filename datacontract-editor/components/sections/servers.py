import streamlit as st
import uuid
from utils.templates import SERVER_TYPES, ENVIRONMENTS
from utils.state import sync_yaml

_SERVER_FIELDS = {
    "databricks": ["catalog", "schema"],
    "bigquery":   ["project", "dataset"],
    "snowflake":  ["account", "database", "schema", "warehouse"],
    "postgres":   ["host", "port", "database", "schema"],
    "sqlserver":  ["host", "port", "database", "schema"],
    "oracle":     ["host", "port", "database", "schema"],
    "s3":         ["location"],
    "azure":      ["location"],
    "gcs":        ["location"],
    "kafka":      ["host", "port"],
    "local":      ["path"],
}

def render():
    st.markdown('<div class="section-header">🖥️ Servers & Environments</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Define los ambientes de datos disponibles: producción, staging, desarrollo, etc.</div>', unsafe_allow_html=True)

    servers = st.session_state["servers"]

    if not servers:
        st.info("No servers defined yet. Click **＋ Add Server** to add an environment.")

    for i, s in enumerate(servers):
        sid = s.get("id", str(i))
        with st.expander(f"🖥️  {s.get('name','(unnamed)')} — {s.get('environment','').upper() or 'ENV?'}", expanded=True):
            c1, c2, c3, c_del = st.columns([3, 3, 2, 1])
            with c1:
                v = st.text_input("Server name *", value=s.get("name",""), key=f"sv_name_{sid}", placeholder="production")
                if v != s.get("name"): s["name"] = v; sync_yaml()
            with c2:
                idx = SERVER_TYPES.index(s.get("type","databricks")) if s.get("type") in SERVER_TYPES else 0
                v = st.selectbox("Type", SERVER_TYPES, index=idx, key=f"sv_type_{sid}")
                if v != s.get("type"): s["type"] = v; sync_yaml()
            with c3:
                env_opts = ENVIRONMENTS
                idx = env_opts.index(s.get("environment","production")) if s.get("environment") in env_opts else 0
                v = st.selectbox("Environment", env_opts, index=idx, key=f"sv_env_{sid}")
                if v != s.get("environment"): s["environment"] = v; sync_yaml()
            with c_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"sv_del_{sid}"):
                    servers.pop(i); sync_yaml(); st.rerun()

            v = st.text_input("Description", value=s.get("description",""), key=f"sv_desc_{sid}",
                              placeholder="Describe this environment")
            if v != s.get("description"): s["description"] = v; sync_yaml()

            # Dynamic fields based on type
            extra_fields = _SERVER_FIELDS.get(s.get("type","databricks"), [])
            if extra_fields:
                cols = st.columns(len(extra_fields))
                for col, field in zip(cols, extra_fields):
                    with col:
                        v = st.text_input(field.capitalize(), value=s.get(field,""), key=f"sv_{field}_{sid}")
                        if v != s.get(field): s[field] = v; sync_yaml()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Server", type="primary", key="btn_add_server"):
        st.session_state["servers"].append({
            "id": str(uuid.uuid4())[:8], "name": "", "type": "databricks",
            "environment": "production", "description": "",
            "catalog": "", "schema": "", "database": "", "host": "",
            "port": "", "project": "", "dataset": "", "account": "",
            "warehouse": "", "path": "", "location": "", "roles": [],
        })
        st.rerun()
