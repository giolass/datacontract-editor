import streamlit as st
from utils.state import sync_yaml

NOTICE_OPTIONS = ["P1M","P3M","P6M","P1Y"]
BILLING_OPTIONS = ["Free","Subscription","Per-use","Enterprise"]

def render():
    st.markdown('<div class="section-header">📜 Terms of Use</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Condiciones de uso, restricciones y acuerdos del contrato.</div>', unsafe_allow_html=True)

    t = st.session_state["terms"]

    v = st.text_area("Usage *", value=t.get("usage",""), height=90, key="t_usage",
                     placeholder="Describe the approved uses for this data contract...")
    if v != t.get("usage"): t["usage"] = v; sync_yaml()

    v = st.text_area("Limitations", value=t.get("limitations",""), height=90, key="t_lim",
                     placeholder="List any restrictions or prohibited uses...")
    if v != t.get("limitations"): t["limitations"] = v; sync_yaml()

    c1, c2 = st.columns(2)
    with c1:
        idx = BILLING_OPTIONS.index(t.get("billing","Free")) if t.get("billing") in BILLING_OPTIONS else 0
        v = st.selectbox("Billing Model", BILLING_OPTIONS, index=idx, key="t_billing")
        if v != t.get("billing"): t["billing"] = v; sync_yaml()
    with c2:
        idx = NOTICE_OPTIONS.index(t.get("noticePeriod","P3M")) if t.get("noticePeriod") in NOTICE_OPTIONS else 1
        v = st.selectbox("Notice Period", NOTICE_OPTIONS, index=idx, key="t_notice",
                         help="ISO 8601 duration: P1M=1 month, P3M=3 months, P1Y=1 year")
        if v != t.get("noticePeriod"): t["noticePeriod"] = v; sync_yaml()
