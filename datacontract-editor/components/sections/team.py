import streamlit as st
import uuid
from utils.templates import ROLE_OPTIONS
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">👥 Team & Ownership</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Define propietarios, stewards y contactos del contrato de datos.</div>', unsafe_allow_html=True)

    tm = st.session_state["team"]

    st.markdown('<div class="subsection-label">Ownership</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        v = st.text_input("Owner / Team *", value=tm.get("owner",""), key="tm_owner",
                          placeholder="e.g. data-engineering")
        if v != tm.get("owner"): tm["owner"] = v; sync_yaml()
    with c2:
        v = st.text_input("Owner Email *", value=tm.get("ownerEmail",""), key="tm_email",
                          placeholder="data-engineering@bpt.com.co")
        if v != tm.get("ownerEmail"): tm["ownerEmail"] = v; sync_yaml()

    c3, c4 = st.columns(2)
    with c3:
        v = st.text_input("Data Product", value=tm.get("dataProduct",""), key="tm_product",
                          placeholder="e.g. orders-platform")
        if v != tm.get("dataProduct"): tm["dataProduct"] = v; sync_yaml()
    with c4:
        v = st.text_input("Domain", value=tm.get("domain",""), key="tm_domain",
                          placeholder="e.g. sales, finance, hr")
        if v != tm.get("domain"): tm["domain"] = v; sync_yaml()

    st.markdown('<div class="subsection-label" style="margin-top:1.25rem">Contacts</div>', unsafe_allow_html=True)
    contacts = tm.get("contacts", [])
    if not contacts:
        st.caption("No contacts added yet.")

    for i, c in enumerate(contacts):
        cid = c.get("id", str(i))
        cc1, cc2, cc3, cc_del = st.columns([3, 3, 2, 1])
        with cc1:
            v = st.text_input("Name", value=c.get("name",""), key=f"ct_name_{cid}", placeholder="Full name")
            if v != c.get("name"): c["name"] = v; sync_yaml()
        with cc2:
            v = st.text_input("Email", value=c.get("email",""), key=f"ct_email_{cid}", placeholder="email@bpt.com.co")
            if v != c.get("email"): c["email"] = v; sync_yaml()
        with cc3:
            role_idx = ROLE_OPTIONS.index(c.get("role","owner")) if c.get("role") in ROLE_OPTIONS else 0
            v = st.selectbox("Role", ROLE_OPTIONS, index=role_idx, key=f"ct_role_{cid}")
            if v != c.get("role"): c["role"] = v; sync_yaml()
        with cc_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✕", key=f"ct_del_{cid}"):
                contacts.pop(i); sync_yaml(); st.rerun()

    if st.button("＋  Add Contact", key="btn_add_contact"):
        contacts.append({"id": str(uuid.uuid4())[:8], "name": "", "email": "", "role": "owner"})
        st.rerun()
