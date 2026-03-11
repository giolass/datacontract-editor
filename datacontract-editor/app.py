"""
Data Contract Editor - Databricks App
Editor visual de Data Contracts (ODCS) desplegado en Databricks Apps
"""

import streamlit as st
import os

st.set_page_config(
    page_title="Data Contract Editor",
    page_icon="📋",
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
from utils.state import init_session_state

init_session_state()

st.markdown("""
<div class="app-header">
  <div class="header-brand">
    <span class="header-icon">⬡</span>
    <div>
      <div class="header-title">Data Contract Editor</div>
      <div class="header-sub">Open Data Contract Standard &nbsp;·&nbsp; Databricks</div>
    </div>
  </div>
  <div class="header-badge">ODCS v3.0</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    render_sidebar()

tab_builder, tab_editor, tab_preview = st.tabs([
    "🧱  Schema Builder",
    "📝  YAML Editor",
    "👁  Preview & Validate",
])

with tab_builder:
    render_schema_builder()

with tab_editor:
    render_editor()

with tab_preview:
    render_preview()
