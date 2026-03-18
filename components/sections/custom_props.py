import streamlit as st, uuid
from utils.state import sync_yaml

SUGGESTED_PROPS = [
    "databricksCatalog", "databricksSchema", "databricksTargetTable",
    "ingestionTool", "sourceSystem", "sourceOwnerTeam",
    "piiClassification", "encryptionRequired", "dataClassification",
    "retentionPolicy", "backupLocation", "monitoringDashboard",
]

def render():
    st.markdown('<div class="section-header">⚙️ Custom Properties</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Propiedades adicionales específicas de la organización, plataforma o pipeline.</div>', unsafe_allow_html=True)

    cp = st.session_state["custom_props"]

    hc = st.columns([3, 5, 1])
    for col, lbl in zip(hc, ["Property","Value",""]):
        col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for i, p in enumerate(cp):
        pid = p.get("id", str(i))
        cc = st.columns([3, 5, 1])
        with cc[0]:
            prop_opts = SUGGESTED_PROPS + ([] if p.get("property","") in SUGGESTED_PROPS else [p.get("property","")])
            if p.get("property","") in prop_opts:
                idx = prop_opts.index(p["property"])
                v = st.selectbox("", prop_opts, index=idx, key=f"cp_prop_{pid}", label_visibility="collapsed")
            else:
                v = st.text_input("", value=p.get("property",""), key=f"cp_prop_{pid}", label_visibility="collapsed")
            if v != p.get("property"): p["property"] = v; sync_yaml()
        with cc[1]:
            v = st.text_input("", value=str(p.get("value","")), key=f"cp_val_{pid}", label_visibility="collapsed", placeholder="Value...")
            if v != str(p.get("value","")): p["value"] = v; sync_yaml()
        with cc[2]:
            if st.button("✕", key=f"cp_del_{pid}"):
                cp.pop(i); sync_yaml(); st.rerun()
    if st.button("＋  Add Property", type="primary", key="btn_add_cp"):
        cp.append({"id": str(uuid.uuid4())[:8], "property": "databricksCatalog", "value": ""})
        sync_yaml(); st.rerun()

    # Databricks integration summary
    db_props = {p["property"]: p["value"] for p in cp if p.get("property","").startswith("databricks")}
    if db_props:
        st.markdown(f"""
        <div class="sla-summary" style="margin-top:1.5rem">
          <div style="font-family:var(--poppins);font-size:0.65rem;font-weight:700;color:var(--purple);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Databricks Target</div>
          {"".join(f'<div class="sla-row"><span>{k}</span><b><code style="font-size:0.72rem;color:var(--blue)">{v}</code></b></div>' for k,v in db_props.items() if v)}
        </div>
        """, unsafe_allow_html=True)
