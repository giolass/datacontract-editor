import streamlit as st
from utils.templates import STATUS_OPTIONS
from utils.state import sync_yaml
import uuid

DOMAIN_OPTIONS  = ["", "DATAENG", "OPE", "COM", "SUF", "ADVANCED"]
TENANT_OPTIONS  = ["BPT", "Avianca"]


def render():
    st.markdown('<div class="section-header">📋 Fundamentals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Identidad del contrato de fuente — estándar, versión, dominio y propósito.</div>', unsafe_allow_html=True)

    f = st.session_state["fundamentals"]

    # ── Row 1: Name + Version + Status ────────────────────────────────────────
    c1, c2, c3 = st.columns([4, 2, 2])
    with c1:
        v = st.text_input("Contract Name *", value=f.get("name",""), key="f_name",
                          placeholder="Oracle Orders Source Contract")
        if v != f.get("name"): f["name"] = v; sync_yaml()
    with c2:
        v = st.text_input("Version *", value=f.get("version","1.0.0"), key="f_version")
        if v != f.get("version"): f["version"] = v; sync_yaml()
    with c3:
        idx = STATUS_OPTIONS.index(f.get("status","draft")) if f.get("status") in STATUS_OPTIONS else 0
        v = st.selectbox("Status", STATUS_OPTIONS, index=idx, key="f_status")
        if v != f.get("status"): f["status"] = v; sync_yaml()

    # ── Row 2: Contract ID (simple, no URN prefix) ─────────────────────────────
    c_id1, c_id2 = st.columns([2, 5])
    with c_id1:
        # Auto-prefix display: show the full ID but let user edit only the simple part
        raw_id = f.get("id", "")
        # Strip urn prefix for display
        PREFIX = "urn:datacontract:bpt:"
        display_id = raw_id[len(PREFIX):] if raw_id.startswith(PREFIX) else raw_id
        v = st.text_input("Contract ID *", value=display_id, key="f_id_simple",
                          placeholder="source-data-contract-0001",
                          help="ID simple del contrato — se almacena como URN internamente")
        full_id = PREFIX + v if v and not v.startswith("urn:") else v
        if full_id != f.get("id"): f["id"] = full_id; sync_yaml()
    with c_id2:
        st.markdown(f"""
        <div style="margin-top:1.75rem; padding:0.45rem 0.75rem; background:var(--gray2);
             border-radius:6px; font-family:'Courier New',monospace; font-size:0.72rem;
             color:var(--gray4); border:1px solid var(--border);">
          <span style="color:var(--gray4)">URN → </span>
          <span style="color:var(--blue)">{f.get("id","urn:datacontract:bpt:...")}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Row 3: Domain (dropdown) + Source + Tenant (dropdown) ─────────────────
    c4, c5, c6 = st.columns(3)
    with c4:
        cur_domain = f.get("domain","")
        if cur_domain not in DOMAIN_OPTIONS:
            DOMAIN_OPTIONS.append(cur_domain)
        idx = DOMAIN_OPTIONS.index(cur_domain)
        v = st.selectbox("Domain *", DOMAIN_OPTIONS, index=idx, key="f_domain",
                         help="Dominio de negocio de la fuente de datos")
        if v != f.get("domain"): f["domain"] = v; sync_yaml()
    with c5:
        v = st.text_input("Source *", value=f.get("dataProduct",""), key="f_source",
                          placeholder="Oracle OCI / SQL Server / S3...",
                          help="Nombre de la fuente — se sincroniza con el alias del Server")
        if v != f.get("dataProduct"):
            f["dataProduct"] = v
            # ── Sync: update first server alias if it matches or is empty ─────
            svs = st.session_state.get("servers", [])
            if svs:
                first = svs[0]
                if not first.get("server","").strip() or first.get("server") == f.get("dataProduct",""):
                    first["server"] = v
            sync_yaml()
    with c6:
        cur_tenant = f.get("tenant","BPT")
        if cur_tenant not in TENANT_OPTIONS:
            TENANT_OPTIONS.append(cur_tenant)
        idx = TENANT_OPTIONS.index(cur_tenant) if cur_tenant in TENANT_OPTIONS else 0
        v = st.selectbox("Tenant *", TENANT_OPTIONS, index=idx, key="f_tenant",
                         help="Organización propietaria del contrato")
        if v != f.get("tenant"): f["tenant"] = v; sync_yaml()

    # ── Description ────────────────────────────────────────────────────────────
    st.markdown('<div class="subsection-label" style="margin-top:1rem">Description</div>', unsafe_allow_html=True)
    for field, label, placeholder in [
        ("purpose",    "Purpose",    "¿Qué datos expone este contrato y para qué?"),
        ("limitations","Limitations","Restricciones: geografía, PII, solo lectura, etc."),
        ("usage",      "Usage",      "Usos aprobados: analítica, ML, reportes..."),
    ]:
        v = st.text_area(label, value=f.get(field,""), height=70, key=f"f_{field}", placeholder=placeholder)
        if v != f.get(field): f[field] = v; sync_yaml()

    # ── Tags ───────────────────────────────────────────────────────────────────
    tags_raw = st.text_input("Tags (comma separated)", value=", ".join(f.get("tags",[])), key="f_tags",
                              placeholder="oracle, sales, ecommerce, source")
    tags_new = [t.strip() for t in tags_raw.split(",") if t.strip()]
    if tags_new != f.get("tags"): f["tags"] = tags_new; sync_yaml()

    # ── Authoritative Definitions ──────────────────────────────────────────────
    st.markdown('<div class="subsection-label" style="margin-top:1rem">Authoritative Definitions</div>', unsafe_allow_html=True)
    auth_defs = f.get("authDefs", [])
    if auth_defs:
        hc = st.columns([2, 4, 3, 1])
        for col, lbl in zip(hc, ["Type", "URL", "Description", ""]):
            col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for i, a in enumerate(auth_defs):
        aid = a.get("id", str(i))
        ac1, ac2, ac3, ac_del = st.columns([2, 4, 3, 1])
        with ac1:
            opts = ["businessDefinition","transformationImplementation","videoTutorial",
                    "tutorial","implementation","privacy-statement","canonical"]
            idx = opts.index(a.get("type","businessDefinition")) if a.get("type") in opts else 0
            v = st.selectbox("", opts, index=idx, key=f"ad_type_{aid}", label_visibility="collapsed")
            if v != a.get("type"): a["type"] = v; sync_yaml()
        with ac2:
            v = st.text_input("", value=a.get("url",""), key=f"ad_url_{aid}",
                              placeholder="https://...", label_visibility="collapsed")
            if v != a.get("url"): a["url"] = v; sync_yaml()
        with ac3:
            v = st.text_input("", value=a.get("description",""), key=f"ad_desc_{aid}",
                              placeholder="Description", label_visibility="collapsed")
            if v != a.get("description"): a["description"] = v; sync_yaml()
        with ac_del:
            if st.button("✕", key=f"ad_del_{aid}"):
                auth_defs.pop(i); sync_yaml(); st.rerun()

    if st.button("＋ Add Reference", key="btn_add_authdef"):
        auth_defs.append({"id": str(uuid.uuid4())[:8],
                          "type": "businessDefinition", "url": "", "description": ""})
        sync_yaml(); st.rerun()

    st.markdown(
        '<div class="info-box">💡 <b>kind</b>: DataContract · <b>apiVersion</b>: v3.1.0 — '
        'campos generados automáticamente por el estándar ODCS.</div>',
        unsafe_allow_html=True
    )
