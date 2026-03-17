import streamlit as st
import os

st.set_page_config(
    page_title="Source Data Contract Editor · BPT",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path) as f:
    css = f.read()

st.markdown(f"""
<style>
{css}
header[data-testid="stHeader"] {{ display: none !important; height: 0 !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
div[data-testid="stToolbar"] {{ display: none !important; }}
#MainMenu, footer {{ display: none !important; }}
.stApp {{ margin-top: 0 !important; padding-top: 0 !important; }}
.stAppViewContainer {{ margin-top: 0 !important; padding-top: 0 !important; }}
.stAppViewContainer > section.main {{ padding-top: 0 !important; }}
.stAppViewContainer > section.main > div.block-container {{
    padding-top: 0 !important; padding-bottom: 0 !important;
    margin-top: 0 !important; max-width: 100% !important;
}}
[data-testid="stSidebar"] {{ display: none !important; }}
</style>
<script>
function fixLayout() {{
    var bc = document.querySelector('.block-container');
    if (bc) {{ bc.style.paddingTop='0'; bc.style.marginTop='0'; }}
    var sec = document.querySelector('.stAppViewContainer > section');
    if (sec) {{ sec.style.paddingTop='0'; sec.style.marginTop='0'; }}
    var hb = document.querySelector('[data-testid="stHorizontalBlock"]');
    if (hb) {{ hb.style.marginTop='0'; hb.style.paddingTop='0'; hb.style.gap='0'; }}
    document.querySelectorAll('[data-testid="stColumn"]').forEach(function(col) {{
        col.style.padding='0';
        col.style.display='flex'; col.style.flexDirection='column'; col.style.justifyContent='flex-start';
        var vb = col.querySelector('[data-testid="stVerticalBlock"]');
        if (vb) {{ vb.style.gap='0'; vb.style.paddingTop='0'; vb.style.justifyContent='flex-start'; }}
    }});
}}
fixLayout(); setTimeout(fixLayout,200); setTimeout(fixLayout,700);
</script>
""", unsafe_allow_html=True)

from utils.state import init_session_state, sync_yaml
from utils.storage import list_contracts, load_contract, save_contract, delete_contract
from utils.validator import validate_yaml
from utils.parser import parse_yaml_to_state
from utils.templates import DEFAULT_CONTRACT

from components.sections import (fundamentals, servers, schemas,
                                  quality, team, sla, custom_props)
from components.debug import render_debug

init_session_state()

BPT_SYMBOL = """<svg width="24" height="24" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ga" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#12d0e6"/>
      <stop offset="100%" style="stop-color:#3c25ec"/>
    </linearGradient>
    <linearGradient id="gb" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3c25ec"/>
      <stop offset="100%" style="stop-color:#7923ef"/>
    </linearGradient>
  </defs>
  <ellipse cx="58" cy="38" rx="28" ry="28" fill="url(#ga)" opacity="0.95"/>
  <ellipse cx="42" cy="82" rx="22" ry="22" fill="url(#gb)" opacity="0.95"/>
  <rect x="36" y="24" width="16" height="72" rx="8" fill="url(#gb)" opacity="0.85"/>
</svg>"""

SECTIONS = [
    ("fundamentals",  "📋", "Fundamentals"),
    ("servers",       "🖥️", "Servers"),
    ("schemas",       "🗄️", "Schema"),
    ("quality",       "✅", "Data Quality"),
    ("team",          "👥", "Team"),
    ("sla",           "⏱️", "SLA"),
    ("custom_props",  "⚙️", "Custom Props"),
]

RENDERERS = {
    "fundamentals":  fundamentals.render,
    "servers":       servers.render,
    "schemas":       schemas.render,
    "quality":       quality.render,
    "team":          team.render,
    "sla":           sla.render,
    "custom_props":  custom_props.render,
    "debug":         render_debug,
}

# ══ 3-COL LAYOUT ═════════════════════════════════════════════════════════════
nav_col, main_col, yaml_col = st.columns([1.5, 4.5, 3], gap="small")

# ── NAV ───────────────────────────────────────────────────────────────────────
with nav_col:
    st.markdown('<div class="nav-panel">', unsafe_allow_html=True)

    active_file = st.session_state.get("active_contract_file") or "New Contract"
    st.markdown(f"""
    <div class="nav-brand">
      <div style="display:flex;align-items:center;gap:0.5rem">
        <div>{BPT_SYMBOL}</div>
        <div>
          <div class="nav-brand-title">Source Data Contract</div>
          <div class="nav-brand-sub">ODCS v3.1.0 · DQX · BPT</div>
        </div>
      </div>
      <div class="nav-active-file">📄 {active_file}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-file-label">CONTRACTS</div>', unsafe_allow_html=True)
    if st.button("＋  New Contract", key="nav_new", use_container_width=True):
        st.session_state["yaml_content"] = DEFAULT_CONTRACT
        parse_yaml_to_state(DEFAULT_CONTRACT)
        st.session_state["active_contract_file"] = None
        st.session_state["validation_result"] = None
        st.rerun()

    files = list_contracts()
    if files:
        st.markdown('<div class="nav-saved-label">SAVED</div>', unsafe_allow_html=True)
        for fname in files[:8]:
            is_active = fname == st.session_state.get("active_contract_file")
            cf, cd = st.columns([5, 1])
            with cf:
                if st.button(f"{'▶ ' if is_active else ''}{fname}", key=f"nav_open_{fname}", use_container_width=True):
                    content = load_contract(fname)
                    if content:
                        st.session_state["yaml_content"] = content
                        parse_yaml_to_state(content)
                        st.session_state["active_contract_file"] = fname
                        st.rerun()
            with cd:
                if st.button("🗑", key=f"nav_del_{fname}"):
                    delete_contract(fname)
                    if st.session_state.get("active_contract_file") == fname:
                        st.session_state["active_contract_file"] = None
                    st.rerun()

    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)
    st.markdown('<div class="nav-section-label">SECTIONS</div>', unsafe_allow_html=True)

    active_sec = st.session_state.get("active_section", "fundamentals")
    for key, icon, label in SECTIONS:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state["active_section"] = key; st.rerun()

    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)
    if st.button("🔍  Diagnostics", key="nav_debug", use_container_width=True):
        st.session_state["active_section"] = "debug"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
with main_col:
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)
    renderer = RENDERERS.get(st.session_state.get("active_section","fundamentals"))
    if renderer: renderer()
    st.markdown('</div>', unsafe_allow_html=True)

# ── YAML PANEL ────────────────────────────────────────────────────────────────
with yaml_col:
    st.markdown('<div class="yaml-panel">', unsafe_allow_html=True)
    st.markdown('<div class="yaml-panel-header">YAML PREVIEW</div>', unsafe_allow_html=True)

    ys1, ys2 = st.columns([4, 1])
    with ys1:
        default_name = st.session_state.get("active_contract_file") or "my-source-contract.yaml"
        save_name = st.text_input("", value=default_name, key="yaml_save_name",
                                  label_visibility="collapsed", placeholder="filename.yaml")
    with ys2:
        if st.button("💾", key="btn_save_yaml", help="Save to Volume"):
            if save_name:
                ok = save_contract(save_name, st.session_state["yaml_content"])
                if ok:
                    st.session_state["active_contract_file"] = save_name
                    st.rerun()

    yb1, yb2, yb3 = st.columns(3)
    with yb1:
        if st.button("✅ Validate", key="btn_val", use_container_width=True):
            result = validate_yaml(st.session_state["yaml_content"])
            st.session_state["validation_result"] = result
    with yb2:
        if st.button("📥 Import", key="btn_import", use_container_width=True):
            parse_yaml_to_state(st.session_state["yaml_content"]); st.rerun()
    with yb3:
        st.download_button("⬇ Download", data=st.session_state["yaml_content"].encode(),
                           file_name=save_name, mime="text/yaml",
                           use_container_width=True, key="btn_dl")

    result = st.session_state.get("validation_result")
    if result:
        if result.is_valid:
            st.markdown(f'<div class="val-banner val-ok">✅ Valid · {len(result.warnings)}w · {len(result.infos)}i</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="val-banner val-fail">❌ {len(result.errors)} error(s)</div>', unsafe_allow_html=True)
        for issue in result.issues[:5]:
            icon = {"error":"🔴","warning":"🟡","info":"🔵"}.get(issue.severity,"⚪")
            st.markdown(f'<div class="val-issue">{icon} <b>{issue.path}</b> — {issue.message}</div>', unsafe_allow_html=True)

    yaml_val = st.text_area("", value=st.session_state["yaml_content"],
                            height=480, key="yaml_raw_editor", label_visibility="collapsed")
    if yaml_val != st.session_state["yaml_content"]:
        st.session_state["yaml_content"] = yaml_val

    uploaded = st.file_uploader("Upload YAML", type=["yaml","yml"],
                                key="yaml_uploader", label_visibility="collapsed")
    if uploaded:
        content = uploaded.read().decode("utf-8")
        st.session_state["yaml_content"] = content
        parse_yaml_to_state(content)
        st.session_state["active_contract_file"] = uploaded.name
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
