import streamlit as st, uuid
from utils.templates import SLA_DRIVERS, SLA_UNITS
from utils.state import sync_yaml

SLA_PROPERTIES = ["availability","freshness","retention","latency","frequency",
                  "support","responseTime","backup","rowCount","columnCount"]

def render():
    st.markdown('<div class="section-header">⏱️ Service Level Agreement</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Garantías de calidad de servicio sobre los datos de la fuente.</div>', unsafe_allow_html=True)

    sla = st.session_state["sla"]

    hc = st.columns([2, 2, 2, 2, 2, 3, 1])
    for col, lbl in zip(hc, ["Property","Value","Unit","Driver","Schedule (cron)","Description / Element",""]):
        col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for i, s in enumerate(sla):
        sid = s.get("id", str(i))
        sc = st.columns([2, 2, 2, 2, 2, 3, 1])
        with sc[0]:
            prop_opts = SLA_PROPERTIES + ([] if s.get("property","") in SLA_PROPERTIES else [s.get("property","")])
            idx = prop_opts.index(s.get("property","availability")) if s.get("property") in prop_opts else 0
            v = st.selectbox("", prop_opts, index=idx, key=f"sl_prop_{sid}", label_visibility="collapsed")
            if v != s.get("property"): s["property"] = v; sync_yaml()
        with sc[1]:
            v = st.text_input("", value=str(s.get("value","")), key=f"sl_val_{sid}", placeholder="99.5 / 1 / daily", label_visibility="collapsed")
            if v != str(s.get("value","")): s["value"] = v; sync_yaml()
        with sc[2]:
            unit_opts = [""] + SLA_UNITS
            idx = unit_opts.index(s.get("unit","")) if s.get("unit") in unit_opts else 0
            v = st.selectbox("", unit_opts, index=idx, key=f"sl_unit_{sid}", label_visibility="collapsed")
            if v != s.get("unit"): s["unit"] = v; sync_yaml()
        with sc[3]:
            idx = SLA_DRIVERS.index(s.get("driver","operational")) if s.get("driver") in SLA_DRIVERS else 0
            v = st.selectbox("", SLA_DRIVERS, index=idx, key=f"sl_drv_{sid}", label_visibility="collapsed")
            if v != s.get("driver"): s["driver"] = v; sync_yaml()
        with sc[4]:
            v = st.text_input("", value=s.get("schedule",""), key=f"sl_sched_{sid}", placeholder="0 1 * * *", label_visibility="collapsed")
            if v != s.get("schedule"): s["schedule"] = v; sync_yaml()
        with sc[5]:
            desc_elem = f"{s.get('description','')} | {s.get('element','')}".strip(" |")
            v = st.text_input("", value=desc_elem, key=f"sl_desc_{sid}", placeholder="Description · table.column", label_visibility="collapsed")
            parts = v.split("|", 1)
            s["description"] = parts[0].strip()
            s["element"] = parts[1].strip() if len(parts) > 1 else ""
            sync_yaml()
        with sc[6]:
            if st.button("✕", key=f"sl_del_{sid}"):
                sla.pop(i); sync_yaml(); st.rerun()
    if st.button("＋  Add SLA Property", type="primary", key="btn_add_sla"):
        sla.append({"id": str(uuid.uuid4())[:8], "property": "availability", "value": "",
                    "unit": "percent", "driver": "operational", "description": "",
                    "element": "", "schedule": ""})
        sync_yaml(); st.rerun()

    # Summary card
    if sla:
        st.markdown('<div class="sla-summary" style="margin-top:1.5rem">', unsafe_allow_html=True)
        rows = "".join(
            f'<div class="sla-row"><span>{s["property"]}</span>'
            f'<b>{s.get("value","")} {s.get("unit","")}</b></div>'
            for s in sla if s.get("property") and s.get("value")
        )
        st.markdown(f'<div class="sla-summary">{rows}</div>', unsafe_allow_html=True)
