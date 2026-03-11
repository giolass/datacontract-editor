import streamlit as st
from utils.templates import STATUS_OPTIONS
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">📋 Fundamentals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Identidad básica del contrato — ID único, versión y clasificación.</div>', unsafe_allow_html=True)

    f = st.session_state["fundamentals"]

    c1, c2, c3 = st.columns([4, 2, 2])
    with c1:
        v = st.text_input("Contract Title *", value=f.get("title",""), key="f_title", placeholder="e.g. Orders Data Contract")
        if v != f.get("title"): f["title"] = v; sync_yaml()
    with c2:
        v = st.text_input("Version *", value=f.get("version","1.0.0"), key="f_version")
        if v != f.get("version"): f["version"] = v; sync_yaml()
    with c3:
        idx = STATUS_OPTIONS.index(f.get("status","draft")) if f.get("status") in STATUS_OPTIONS else 0
        v = st.selectbox("Status", STATUS_OPTIONS, index=idx, key="f_status")
        if v != f.get("status"): f["status"] = v; sync_yaml()

    v = st.text_input("Contract ID (URN) *", value=f.get("id",""), key="f_id",
                      placeholder="urn:datacontract:bpt:domain:name")
    if v != f.get("id"): f["id"] = v; sync_yaml()

    v = st.text_area("Description", value=f.get("description",""), height=100, key="f_desc",
                     placeholder="What data does this contract expose? Who are the consumers?")
    if v != f.get("description"): f["description"] = v; sync_yaml()

    tags_raw = st.text_input("Tags (comma separated)", value=", ".join(f.get("tags",[])), key="f_tags",
                             placeholder="orders, ecommerce, sales")
    tags_new = [t.strip() for t in tags_raw.split(",") if t.strip()]
    if tags_new != f.get("tags"): f["tags"] = tags_new; sync_yaml()

    st.markdown('<div class="info-box">💡 El <b>Contract ID</b> debe seguir el formato URN: <code>urn:datacontract:&lt;org&gt;:&lt;dominio&gt;:&lt;nombre&gt;</code></div>', unsafe_allow_html=True)
