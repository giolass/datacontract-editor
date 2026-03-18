import streamlit as st, uuid
from utils.templates import SERVER_TYPES, ENVIRONMENTS, SERVER_FIELDS, ACCESS_TYPES
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">🖥️ Servers & Environments</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Conexión física a los ambientes de la fuente de datos (producción, dev, QA).</div>', unsafe_allow_html=True)

    servers = st.session_state["servers"]
    if not servers:
        st.info("Sin servidores definidos. Haz clic en **＋ Add Server**.")

    for i, s in enumerate(servers):
        sid = s.get("id", str(i))
        stype = s.get("type","oracle")
        label = f"🖥️  **{s.get('server','(sin nombre)')}** — {stype.upper()} · {s.get('environment','').upper()}"
        with st.expander(label, expanded=i == 0):
            # Row 1
            c1, c2, c3, c_del = st.columns([3, 3, 3, 1])
            with c1:
                v = st.text_input("Server alias *", value=s.get("server",""), key=f"sv_name_{sid}", placeholder="production")
                if v != s.get("server"):
                    s["server"] = v
                    # Sync first server name → Fundamentals Source field
                    if i == 0:
                        st.session_state["fundamentals"]["dataProduct"] = v
                    sync_yaml()
            with c2:
                idx = SERVER_TYPES.index(stype) if stype in SERVER_TYPES else 0
                v = st.selectbox("Type", SERVER_TYPES, index=idx, key=f"sv_type_{sid}")
                if v != s.get("type"): s["type"] = v; sync_yaml(); st.rerun()
            with c3:
                idx = ENVIRONMENTS.index(s.get("environment","production")) if s.get("environment") in ENVIRONMENTS else 0
                v = st.selectbox("Environment", ENVIRONMENTS, index=idx, key=f"sv_env_{sid}")
                if v != s.get("environment"): s["environment"] = v; sync_yaml()
            with c_del:
                if st.button("🗑", key=f"sv_del_{sid}"):
                    servers.pop(i); sync_yaml(); st.rerun()

            # Description
            v = st.text_input("Description", value=s.get("description",""), key=f"sv_desc_{sid}",
                              placeholder="Describe this environment")
            if v != s.get("description"): s["description"] = v; sync_yaml()

            # Dynamic connection fields
            fields = SERVER_FIELDS.get(s.get("type","oracle"), ["host","port","database","schema"])
            cols = st.columns(len(fields))
            for col, field in zip(cols, fields):
                with col:
                    v = st.text_input(field.capitalize(), value=str(s.get(field,"")), key=f"sv_{field}_{sid}")
                    if v != str(s.get(field,"")): s[field] = v; sync_yaml()

            # Roles
            st.markdown('<div class="subsection-label" style="margin-top:0.75rem">Access Roles</div>', unsafe_allow_html=True)
            roles = s.get("roles", [])
            for j, r in enumerate(roles):
                rc1, rc2, rc_del = st.columns([3, 5, 1])
                with rc1:
                    idx = ACCESS_TYPES.index(r.get("role","read")) if r.get("role") in ACCESS_TYPES else 0
                    v = st.selectbox("", ACCESS_TYPES, index=idx, key=f"sv_rl_{sid}_{j}", label_visibility="collapsed")
                    if v != r.get("role"): r["role"] = v; sync_yaml()
                with rc2:
                    groups = ", ".join(r.get("groups", []))
                    v = st.text_input("", value=groups, key=f"sv_grp_{sid}_{j}", placeholder="data-engineering, analysts", label_visibility="collapsed")
                    new_groups = [g.strip() for g in v.split(",") if g.strip()]
                    if new_groups != r.get("groups",[]): r["groups"] = new_groups; sync_yaml()
                with rc_del:
                    if st.button("✕", key=f"sv_rl_del_{sid}_{j}"):
                        roles.pop(j); sync_yaml(); st.rerun()

            if st.button("＋ Add Role", key=f"sv_add_role_{sid}"):
                roles.append({"role": "read", "groups": []}); sync_yaml(); st.rerun()
    if st.button("＋  Add Server", type="primary", key="btn_add_server"):
        servers.append({
            "id": str(uuid.uuid4())[:8], "server": "", "type": "oracle",
            "environment": "production", "description": "",
            "host": "", "port": "1521", "database": "", "schema": "",
            "catalog": "", "project": "", "dataset": "", "account": "",
            "warehouse": "", "location": "", "path": "", "roles": [],
        })
        st.rerun()
