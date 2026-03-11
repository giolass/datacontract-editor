import streamlit as st
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">🎧 Support</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Canales de soporte y documentación para los consumidores del contrato.</div>', unsafe_allow_html=True)

    sp = st.session_state["support"]

    c1, c2 = st.columns(2)
    with c1:
        v = st.text_input("Slack / Teams Channel", value=sp.get("channel",""), key="sp_channel",
                          placeholder="#data-contracts")
        if v != sp.get("channel"): sp["channel"] = v; sync_yaml()
    with c2:
        v = st.text_input("Support URL", value=sp.get("url",""), key="sp_url",
                          placeholder="https://support.bpt.com.co")
        if v != sp.get("url"): sp["url"] = v; sync_yaml()

    c3, c4 = st.columns(2)
    with c3:
        v = st.text_input("On-call Email", value=sp.get("on_call",""), key="sp_oncall",
                          placeholder="data-oncall@bpt.com.co")
        if v != sp.get("on_call"): sp["on_call"] = v; sync_yaml()
    with c4:
        v = st.text_input("Documentation URL", value=sp.get("doc_url",""), key="sp_doc",
                          placeholder="https://docs.bpt.com.co/data-contracts")
        if v != sp.get("doc_url"): sp["doc_url"] = v; sync_yaml()
