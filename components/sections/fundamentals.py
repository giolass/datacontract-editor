import streamlit as st
from utils.templates import STATUS_OPTIONS
from utils.state import sync_yaml
import uuid


def render():
    st.markdown('<div class="section-header">📋 Fundamentals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Identidad del contrato de fuente — estándar, versión, dominio y propósito.</div>', unsafe_allow_html=True)

    f = st.session_state["fundamentals"]

    # Row 1: Name + Version + Status
    c1, c2, c3 = st.columns([4, 2, 2])
    with c1:
        v = st.text_input("Contract Name *", value=f.get("name",""), key="f_name", placeholder="Oracle Orders Source Contract")
        if v != f.get("name"): f["name"] = v; sync_yaml()
    with c2:
        v = st.text_input("Version *", value=f.get("version","1.0.0"), key="f_version")
        if v != f.get("version"): f["version"] = v; sync_yaml()
    with c3:
        idx = STATUS_OPTIONS.index(f.get("status","draft")) if f.get("status") in STATUS_OPTIONS else 0
        v = st.selectbox("Status", STATUS_OPTIONS, index=idx, key="f_status")
        if v != f.get("status"): f["status"] = v; sync_yaml()

    # Row 2: ID
    v = st.text_input("Contract ID (URN) *", value=f.get("id",""), key="f_id",
                      placeholder="urn:datacontract:bpt:domain:source-name")
    if v != f.get("id"): f["id"] = v; sync_yaml()

    # Row 3: Domain + DataProduct + Tenant
    c4, c5, c6 = st.columns(3)
    with c4:
        v = st.text_input("Domain", value=f.get("domain",""), key="f_domain", placeholder="sales")
        if v != f.get("domain"): f["domain"] = v; sync_yaml()
    with c5:
        v = st.text_input("Data Product", value=f.get("dataProduct",""), key="f_dp", placeholder="orders-platform")
        if v != f.get("dataProduct"): f["dataProduct"] = v; sync_yaml()
    with c6:
        v = st.text_input("Tenant", value=f.get("tenant","BPT"), key="f_tenant")
        if v != f.get("tenant"): f["tenant"] = v; sync_yaml()

    st.markdown('<div class="subsection-label" style="margin-top:1rem">Description</div>', unsafe_allow_html=True)
    for field, label, placeholder in [
        ("purpose",    "Purpose",    "What data does this contract expose and why?"),
        ("limitations","Limitations","Restrictions: geography, PII, read-only, etc."),
        ("usage",      "Usage",      "Approved uses: analytics, ML, reporting..."),
    ]:
        v = st.text_area(label, value=f.get(field,""), height=75, key=f"f_{field}", placeholder=placeholder)
        if v != f.get(field): f[field] = v; sync_yaml()

    # Tags
    tags_raw = st.text_input("Tags (comma separated)", value=", ".join(f.get("tags",[])), key="f_tags",
                              placeholder="oracle, sales, ecommerce, source")
    tags_new = [t.strip() for t in tags_raw.split(",") if t.strip()]
    if tags_new != f.get("tags"): f["tags"] = tags_new; sync_yaml()

    # Authoritative definitions
    st.markdown('<div class="subsection-label" style="margin-top:1rem">Authoritative Definitions</div>', unsafe_allow_html=True)
    auth_defs = f.get("authDefs", [])
    for i, a in enumerate(auth_defs):
        aid = a.get("id", str(i))
        ac1, ac2, ac3, ac_del = st.columns([2, 4, 3, 1])
        with ac1:
            opts = ["businessDefinition","transformationImplementation","videoTutorial","tutorial","implementation","privacy-statement","canonical"]
            idx = opts.index(a.get("type","businessDefinition")) if a.get("type") in opts else 0
            v = st.selectbox("Type", opts, index=idx, key=f"ad_type_{aid}", label_visibility="collapsed")
            if v != a.get("type"): a["type"] = v; sync_yaml()
        with ac2:
            v = st.text_input("", value=a.get("url",""), key=f"ad_url_{aid}", placeholder="https://...", label_visibility="collapsed")
            if v != a.get("url"): a["url"] = v; sync_yaml()
        with ac3:
            v = st.text_input("", value=a.get("description",""), key=f"ad_desc_{aid}", placeholder="Description", label_visibility="collapsed")
            if v != a.get("description"): a["description"] = v; sync_yaml()
        with ac_del:
            if st.button("✕", key=f"ad_del_{aid}"):
                auth_defs.pop(i); sync_yaml(); st.rerun()
    if st.button("＋ Add Reference", key="btn_add_authdef"):
        auth_defs.append({"id": str(uuid.uuid4())[:8], "type": "businessDefinition", "url": "", "description": ""})
        sync_yaml(); st.rerun()

    st.markdown('<div class="info-box">💡 <b>kind</b>: DataContract · <b>apiVersion</b>: v3.1.0 (ODCS standard fields, auto-generated)</div>', unsafe_allow_html=True)
