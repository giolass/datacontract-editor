"""Sidebar: contract management (new / open / save / delete)."""
import streamlit as st
from utils.storage import list_contracts, load_contract, save_contract, delete_contract
from utils.parser import parse_yaml_to_state
from utils.templates import DEFAULT_CONTRACT, STATUS_OPTIONS
import os


def render_sidebar():
    st.markdown('<div class="sidebar-section-title">📁 Contracts</div>', unsafe_allow_html=True)

    # ── New contract ──────────────────────────────────────────────────────────
    if st.button("＋  New Contract", use_container_width=True, key="btn_new"):
        st.session_state["yaml_content"] = DEFAULT_CONTRACT
        parse_yaml_to_state(DEFAULT_CONTRACT)
        st.session_state["active_contract_file"] = None
        st.session_state["validation_result"] = None
        st.rerun()

    st.divider()

    # ── Save current contract ─────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Save as</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        default_name = st.session_state.get("active_contract_file") or "my-contract.yaml"
        save_name = st.text_input("Filename", value=default_name,
                                  label_visibility="collapsed", key="save_name_input")
    with col2:
        if st.button("💾", key="btn_save", help="Save contract"):
            if save_name:
                ok = save_contract(save_name, st.session_state["yaml_content"])
                if ok:
                    st.session_state["active_contract_file"] = save_name
                    st.success("Saved!")
                    st.rerun()

    st.divider()

    # ── Load existing contracts ───────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Open saved</div>', unsafe_allow_html=True)
    files = list_contracts()
    if not files:
        st.caption("No contracts saved yet.")
    else:
        for fname in files:
            is_active = fname == st.session_state.get("active_contract_file")
            label = f"{'▶ ' if is_active else ''}{fname}"
            col_f, col_del = st.columns([5, 1])
            with col_f:
                if st.button(label, key=f"open_{fname}", use_container_width=True):
                    content = load_contract(fname)
                    if content:
                        st.session_state["yaml_content"] = content
                        parse_yaml_to_state(content)
                        st.session_state["active_contract_file"] = fname
                        st.session_state["validation_result"] = None
                        st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{fname}", help=f"Delete {fname}"):
                    delete_contract(fname)
                    if st.session_state.get("active_contract_file") == fname:
                        st.session_state["active_contract_file"] = None
                    st.rerun()

    st.divider()

    # ── Upload YAML ───────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Upload YAML</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload .yaml", type=["yaml", "yml"],
                                label_visibility="collapsed", key="file_uploader")
    if uploaded:
        content = uploaded.read().decode("utf-8")
        st.session_state["yaml_content"] = content
        parse_yaml_to_state(content)
        st.session_state["active_contract_file"] = uploaded.name
        st.session_state["validation_result"] = None
        st.rerun()

    st.divider()

    # ── Download current YAML ─────────────────────────────────────────────────
    fname_dl = st.session_state.get("active_contract_file") or "contract.yaml"
    st.download_button(
        label="⬇  Download YAML",
        data=st.session_state["yaml_content"].encode("utf-8"),
        file_name=fname_dl,
        mime="text/yaml",
        use_container_width=True,
        key="btn_download",
    )

    st.divider()
    st.caption("Data Contract Editor v1.0\nODCS 1.1.0 compatible")
