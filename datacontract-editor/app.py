import streamlit as st
import os

st.set_page_config(
    page_title="Data Contract Editor · BPT",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⬡</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from components.editor import render_editor
from components.schema_builder import render_schema_builder
from components.preview import render_preview
from components.debug import render_debug
from utils.state import init_session_state

init_session_state()

# BPT Symbol SVG (recreated from brand manual colors)
BPT_SYMBOL = """
<svg width="36" height="36" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#12d0e6"/>
      <stop offset="100%" style="stop-color:#3c25ec"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3c25ec"/>
      <stop offset="100%" style="stop-color:#7923ef"/>
    </linearGradient>
  </defs>
  <!-- Top loop (cyan-blue) -->
  <path d="M55 15 C55 15 75 15 75 35 C75 55 55 55 55 55 L45 55 C45 55 25 55 25 35 C25 15 45 15 55 15Z"
        fill="url(#g1)" opacity="0.95"/>
  <!-- Bottom loop (purple) -->  
  <path d="M45 55 C45 55 65 55 65 70 C65 85 50 90 40 82 C30 74 30 60 45 55Z"
        fill="url(#g2)" opacity="0.95"/>
  <path d="M35 48 C35 48 55 45 55 55 C55 65 40 70 35 65 C25 58 25 48 35 48Z"
        fill="url(#g2)" opacity="0.85"/>
</svg>
"""

st.markdown(f"""
<div class="app-header">
  <div class="header-brand">
    <div class="bpt-symbol">{BPT_SYMBOL}</div>
    <div>
      <div class="header-title">Data Contract Editor</div>
      <div class="header-sub">Open Data Contract Standard &nbsp;·&nbsp; Databricks</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-badge">ODCS v1.1.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    # BPT logo in sidebar
    st.markdown(f"""
    <div style="padding: 1rem 0.5rem 0.5rem; border-bottom: 1px solid #dde0f0; margin-bottom: 0.75rem;">
      <div style="display:flex; align-items:center; gap:0.6rem;">
        <div style="width:28px">{BPT_SYMBOL}</div>
        <div>
          <div style="font-family:'Poppins',sans-serif; font-weight:700; font-size:0.9rem; color:#09073e; letter-spacing:0.05em;">BPT</div>
          <div style="font-size:0.62rem; color:#8b8fad; text-transform:uppercase; letter-spacing:0.08em;">Data Platform</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    render_sidebar()

tab_builder, tab_editor, tab_preview, tab_debug = st.tabs([
    "🧱  Schema Builder",
    "📝  YAML Editor",
    "👁  Preview & Validate",
    "🔍  Diagnostics",
])

with tab_builder:
    render_schema_builder()

with tab_editor:
    render_editor()

with tab_preview:
    render_preview()

with tab_debug:
    render_debug()
