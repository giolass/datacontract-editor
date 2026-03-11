import streamlit as st
from utils.state import sync_yaml

BILLING_OPTIONS = ["Free", "Subscription", "Per-use", "Enterprise", "Internal chargeback"]
CURRENCY_OPTIONS = ["USD", "EUR", "COP", "GBP"]
UNIT_OPTIONS     = ["per month", "per year", "per query", "per GB", "per user"]


def render():
    st.markdown('<div class="section-header">💰 Pricing</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Modelo de cobro y costos asociados al consumo de este contrato.</div>', unsafe_allow_html=True)

    pr = st.session_state["pricing"]

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    with c1:
        idx = BILLING_OPTIONS.index(pr.get("billing","Free")) if pr.get("billing") in BILLING_OPTIONS else 0
        v = st.selectbox("Billing Model", BILLING_OPTIONS, index=idx, key="pr_billing")
        if v != pr.get("billing"): pr["billing"] = v; sync_yaml()
    with c2:
        v = st.text_input("Amount", value=pr.get("price_amount",""), key="pr_amount",
                          placeholder="0.00")
        if v != pr.get("price_amount"): pr["price_amount"] = v; sync_yaml()
    with c3:
        idx = CURRENCY_OPTIONS.index(pr.get("price_currency","USD")) if pr.get("price_currency") in CURRENCY_OPTIONS else 0
        v = st.selectbox("Currency", CURRENCY_OPTIONS, index=idx, key="pr_currency")
        if v != pr.get("price_currency"): pr["price_currency"] = v; sync_yaml()
    with c4:
        idx = UNIT_OPTIONS.index(pr.get("price_unit","per month")) if pr.get("price_unit") in UNIT_OPTIONS else 0
        v = st.selectbox("Unit", UNIT_OPTIONS, index=idx, key="pr_unit")
        if v != pr.get("price_unit"): pr["price_unit"] = v; sync_yaml()

    if pr.get("billing") == "Free":
        st.success("✅ Este contrato es de acceso gratuito para los consumidores aprobados.")
