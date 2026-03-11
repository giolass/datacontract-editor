import streamlit as st
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">⏱️ Service Level Agreement (SLA)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Define las garantías de calidad, disponibilidad y tiempos de respuesta del contrato.</div>', unsafe_allow_html=True)

    sl = st.session_state["sla"]

    # Availability + Freshness
    st.markdown('<div class="subsection-label">Availability & Freshness</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        v = st.text_input("Availability %", value=sl.get("availability","99.9%"), key="sl_avail",
                          help="e.g. 99.9%")
        if v != sl.get("availability"): sl["availability"] = v; sync_yaml()
    with c2:
        v = st.text_input("Freshness Threshold", value=sl.get("freshness_threshold","1h"), key="sl_fresh",
                          help="ISO 8601 duration: 1h, 30m, 1d")
        if v != sl.get("freshness_threshold"): sl["freshness_threshold"] = v; sync_yaml()
    with c3:
        v = st.text_input("Retention Period", value=sl.get("retention","1 year"), key="sl_retention",
                          help="e.g. 1 year, 6 months, 5 years")
        if v != sl.get("retention"): sl["retention"] = v; sync_yaml()

    v = st.text_input("Freshness Description", value=sl.get("freshness_description",""), key="sl_fresh_desc",
                      placeholder="e.g. Data updated every hour via Spark streaming job")
    if v != sl.get("freshness_description"): sl["freshness_description"] = v; sync_yaml()

    # Latency + Support
    st.markdown('<div class="subsection-label" style="margin-top:1rem">Latency & Support</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        v = st.text_input("Query Latency", value=sl.get("latency",""), key="sl_latency",
                          placeholder="e.g. 5s, 100ms")
        if v != sl.get("latency"): sl["latency"] = v; sync_yaml()
    with c5:
        opts = ["9x5","24x7","8x5","Business hours"]
        idx = opts.index(sl.get("support_time","9x5")) if sl.get("support_time") in opts else 0
        v = st.selectbox("Support Hours", opts, index=idx, key="sl_sup_time")
        if v != sl.get("support_time"): sl["support_time"] = v; sync_yaml()
    with c6:
        v = st.text_input("Response Time", value=sl.get("support_response","1h"), key="sl_sup_resp",
                          help="e.g. 1h, 4h, 24h")
        if v != sl.get("support_response"): sl["support_response"] = v; sync_yaml()

    # Backup
    st.markdown('<div class="subsection-label" style="margin-top:1rem">Backup & Recovery</div>', unsafe_allow_html=True)
    cb1, cb2 = st.columns(2)
    with cb1:
        v = st.text_input("Backup Frequency", value=sl.get("backup_time",""), key="sl_bkp_time",
                          placeholder="e.g. daily, 6h")
        if v != sl.get("backup_time"): sl["backup_time"] = v; sync_yaml()
    with cb2:
        v = st.text_input("Recovery Time (RTO)", value=sl.get("backup_recovery",""), key="sl_bkp_rto",
                          placeholder="e.g. 4h, 24h")
        if v != sl.get("backup_recovery"): sl["backup_recovery"] = v; sync_yaml()

    # SLA Summary card
    st.markdown(f"""
    <div class="sla-summary">
      <div class="sla-row"><span>📶 Availability</span><b>{sl.get('availability','—')}</b></div>
      <div class="sla-row"><span>🔄 Freshness</span><b>{sl.get('freshness_threshold','—')}</b></div>
      <div class="sla-row"><span>🗄️ Retention</span><b>{sl.get('retention','—')}</b></div>
      <div class="sla-row"><span>⚡ Latency</span><b>{sl.get('latency','—')}</b></div>
      <div class="sla-row"><span>🎧 Support</span><b>{sl.get('support_time','—')} · {sl.get('support_response','—')}</b></div>
    </div>
    """, unsafe_allow_html=True)
