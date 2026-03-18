import streamlit as st
import uuid
from utils.templates import ACCESS_TYPES
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">🔐 Roles & Access</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Define los roles de acceso y sus niveles de permisos sobre los datos.</div>', unsafe_allow_html=True)

    roles = st.session_state["roles"]

    if not roles:
        st.info("No roles defined yet. Click **＋ Add Role** to define access levels.")

    for i, r in enumerate(roles):
        rid = r.get("id", str(i))
        with st.container():
            c1, c2, c3, c_del = st.columns([3, 2, 5, 1])
            with c1:
                v = st.text_input("Role name *", value=r.get("name",""), key=f"rl_name_{rid}",
                                  placeholder="e.g. analyst")
                if v != r.get("name"): r["name"] = v; sync_yaml()
            with c2:
                idx = ACCESS_TYPES.index(r.get("access","read")) if r.get("access") in ACCESS_TYPES else 0
                v = st.selectbox("Access", ACCESS_TYPES, index=idx, key=f"rl_access_{rid}")
                if v != r.get("access"): r["access"] = v; sync_yaml()
            with c3:
                v = st.text_input("Description", value=r.get("description",""), key=f"rl_desc_{rid}",
                                  placeholder="What can this role do?")
                if v != r.get("description"): r["description"] = v; sync_yaml()
            with c_del:
                if st.button("✕", key=f"rl_del_{rid}"):
                    roles.pop(i); sync_yaml(); st.rerun()
            st.markdown('<hr style="margin:0.3rem 0; border-color:#dde0f0">', unsafe_allow_html=True)
    if st.button("＋  Add Role", type="primary", key="btn_add_role"):
        roles.append({"id": str(uuid.uuid4())[:8], "name": "", "access": "read", "description": ""})
        st.rerun()
