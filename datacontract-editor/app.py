import streamlit as st
import os

st.set_page_config(
    page_title="Data Contract Editor · BPT",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal CSS — no custom layout divs ──────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path) as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from utils.state import init_session_state, sync_yaml
from utils.storage import list_contracts, load_contract, save_contract, delete_contract
from utils.validator import validate_yaml
from utils.parser import parse_yaml_to_state
from utils.templates import DEFAULT_CONTRACT
from components.sections import (fundamentals, terms, schemas,
                                 servers, team, support, roles, pricing, sla)
from components.debug import render_debug

init_session_state()

SECTIONS = [
    ("fundamentals", "📋", "Fundamentals"),
    ("terms",        "📜", "Terms of Use"),
    ("schemas",      "🗄️", "Schemas"),
    ("servers",      "🖥️", "Servers"),
    ("team",         "👥", "Team"),
    ("support",      "🎧", "Support"),
    ("roles",        "🔐", "Roles"),
    ("pricing",      "💰", "Pricing"),
    ("sla",          "⏱️", "SLA"),
]

RENDERERS = {
    "fundamentals": fundamentals.render,
    "terms":        terms.render,
    "schemas":      schemas.render,
    "servers":      servers.render,
    "team":         team.render,
    "support":      support.render,
    "roles":        roles.render,
    "pricing":      pricing.render,
    "sla":          sla.render,
    "debug":        render_debug,
}

BPT_SVG = """<svg width="22" height="22" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="ga" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#12d0e6"/><stop offset="100%" style="stop-color:#3c25ec"/></linearGradient><linearGradient id="gb" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3c25ec"/><stop offset="100%" style="stop-color:#7923ef"/></linearGradient></defs><ellipse cx="58" cy="38" rx="28" ry="28" fill="url(#ga)"/><ellipse cx="42" cy="82" rx="22" ry="22" fill="url(#gb)"/><rect x="36" y="24" width="16" height="72" rx="8" fill="url(#gb)" opacity="0.85"/></svg>"""

# ── 3-COLUMN LAYOUT ───────────────────────────────────────────────────────────
nav_col, main_col, yaml_col = st.columns([1.5, 4.5, 3], gap="small")

# ═══ LEFT NAV ═════════════════════════════════════════════════════════════════
with nav_col:
    active_file = st.session_state.get("active_contract_file") or "New Contract"
    st.markdown(f"""<div class="nav-brand">
      <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem">
        {BPT_SVG}
        <div>
          <div class="nav-brand-title">Data Contract Editor</div>
          <div class="nav-brand-sub">ODCS 1.1.0 · BPT</div>
        </div>
      </div>
      <div class="nav-active-file">📄 {active_file}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<p class="nav-label">CONTRACTS</p>', unsafe_allow_html=True)
    if st.button("＋  New Contract", key="nav_new", use_container_width=True):
        st.session_state["yaml_content"] = DEFAULT_CONTRACT
        parse_yaml_to_state(DEFAULT_CONTRACT)
        st.session_state["active_contract_file"] = None
        st.rerun()

    files = list_contracts()
    if files:
        st.markdown('<p class="nav-label">SAVED</p>', unsafe_allow_html=True)
        for fname in files[:8]:
            is_active = fname == st.session_state.get("active_contract_file")
            c1, c2 = st.columns([5, 1])
            with c1:
                if st.button(f"{'▶ ' if is_active else ''}{fname}", key=f"open_{fname}", use_container_width=True):
                    content = load_contract(fname)
                    if content:
                        st.session_state["yaml_content"] = content
                        parse_yaml_to_state(content)
                        st.session_state["active_contract_file"] = fname
                        st.rerun()
            with c2:
                if st.button("🗑", key=f"del_{fname}"):
                    delete_contract(fname)
                    st.rerun()

    st.divider()
    st.markdown('<p class="nav-label">SECTIONS</p>', unsafe_allow_html=True)

    active_sec = st.session_state.get("active_section", "fundamentals")
    for key, icon, label in SECTIONS:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True,
                     type="primary" if key == active_sec else "secondary"):
            st.session_state["active_section"] = key
            st.rerun()

    st.divider()
    if st.button("🔍  Diagnostics", key="nav_debug", use_container_width=True,
                 type="primary" if active_sec == "debug" else "secondary"):
        st.session_state["active_section"] = "debug"
        st.rerun()

# ═══ MAIN CONTENT ═════════════════════════════════════════════════════════════
with main_col:
    renderer = RENDERERS.get(active_sec)
    if renderer:
        renderer()

# ═══ YAML PANEL ═══════════════════════════════════════════════════════════════
with yaml_col:
    st.markdown('<p class="yaml-label">YAML PREVIEW</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        default_name = st.session_state.get("active_contract_file") or "my-contract.yaml"
        save_name = st.text_input("filename", value=default_name, key="yaml_save_name",
                                  label_visibility="collapsed")
    with c2:
        if st.button("💾", key="btn_save", help="Save"):
            ok = save_contract(save_name, st.session_state["yaml_content"])
            if ok:
                st.session_state["active_contract_file"] = save_name
                st.rerun()

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("✅ Validate", use_container_width=True, key="btn_val"):
            st.session_state["validation_result"] = validate_yaml(st.session_state["yaml_content"])
    with b2:
        if st.button("📥 Import", use_container_width=True, key="btn_import"):
            parse_yaml_to_state(st.session_state["yaml_content"])
            st.rerun()
    with b3:
        st.download_button("⬇ Download", data=st.session_state["yaml_content"].encode(),
                           file_name=save_name, mime="text/yaml",
                           use_container_width=True, key="btn_dl")

    result = st.session_state.get("validation_result")
    if result:
        if result.is_valid:
            st.success(f"✅ Valid · {len(result.warnings)} warnings")
        else:
            st.error(f"❌ {len(result.errors)} error(s)")
        for issue in result.issues[:5]:
            icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            st.markdown(f'<div class="val-issue">{icon} <b>{issue.path}</b> — {issue.message}</div>',
                        unsafe_allow_html=True)

    st.text_area("yaml", value=st.session_state["yaml_content"],
                 height=520, key="yaml_editor", label_visibility="collapsed")

    uploaded = st.file_uploader("Upload", type=["yaml", "yml"],
                                key="yaml_upload", label_visibility="collapsed")
    if uploaded:
        content = uploaded.read().decode("utf-8")
        st.session_state["yaml_content"] = content
        parse_yaml_to_state(content)
        st.session_state["active_contract_file"] = uploaded.name
        st.rerun()
