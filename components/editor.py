"""
YAML Editor tab — raw YAML editing with syntax awareness.
"""
import streamlit as st
from utils.parser import parse_yaml_to_state
from utils.validator import validate_yaml


def render_editor():
    col_ed, col_help = st.columns([3, 1])

    with col_help:
        st.markdown('<div class="section-header">Quick Reference</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="help-block">
<b>Required keys</b><br>
<code>dataContractSpecification</code><br>
<code>id</code> (URN format)<br>
<code>info.title</code><br>
<code>info.version</code><br>
<code>info.owner</code><br><br>

<b>Field types</b><br>
string · integer · long<br>
float · double · boolean<br>
date · timestamp · bytes<br>
array · object · record<br><br>

<b>Status values</b><br>
draft · active<br>
deprecated · retired<br><br>

<b>Docs</b><br>
<a href="https://datacontract.com" target="_blank">datacontract.com</a>
</div>
""", unsafe_allow_html=True)

    with col_ed:
        st.markdown('<div class="section-header">YAML Editor</div>', unsafe_allow_html=True)
        yaml_val = st.text_area(
            label="Contract YAML",
            value=st.session_state["yaml_content"],
            height=580,
            key="yaml_editor_area",
            label_visibility="collapsed",
            help="Edit the ODCS YAML contract directly. Changes sync to Schema Builder on validate.",
        )
        if yaml_val != st.session_state["yaml_content"]:
            st.session_state["yaml_content"] = yaml_val

        col_btn1, col_btn2, _ = st.columns([2, 2, 4])
        with col_btn1:
            if st.button("✅  Validate", type="primary", key="btn_validate_editor"):
                result = validate_yaml(st.session_state["yaml_content"])
                st.session_state["validation_result"] = result
                # Also sync to builder
                parse_yaml_to_state(st.session_state["yaml_content"])
        with col_btn2:
            if st.button("🔄  Sync to Builder", key="btn_sync_to_builder"):
                parse_yaml_to_state(st.session_state["yaml_content"])
                st.success("Synced to Schema Builder!")
                st.rerun()

    # Inline validation results below editor
    result = st.session_state.get("validation_result")
    if result:
        _render_validation(result)


def _render_validation(result):
    st.markdown("<br>", unsafe_allow_html=True)
    if result.is_valid:
        st.markdown(
            '<div class="val-banner val-ok">✅  Contract is valid — '
            f'{len(result.warnings)} warnings, {len(result.infos)} suggestions</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="val-banner val-fail">❌  {len(result.errors)} error(s) found — '
            f'contract is invalid</div>',
            unsafe_allow_html=True,
        )

    for issue in result.issues:
        icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
        tag_cls = {"error": "tag-error", "warning": "tag-warn", "info": "tag-info"}.get(issue.severity, "")
        st.markdown(
            f'<div class="val-issue">'
            f'{icon} <span class="val-path">{issue.path}</span> '
            f'<span class="{tag_cls}">{issue.severity.upper()}</span> '
            f'— {issue.message}</div>',
            unsafe_allow_html=True,
        )
