"""Session state initialization and helpers."""
import streamlit as st
from utils.templates import DEFAULT_CONTRACT


def init_session_state():
    defaults = {
        "yaml_content": DEFAULT_CONTRACT,
        "contract_meta": {
            "id": "urn:datacontract:com:example:orders",
            "version": "1.0.0",
            "title": "Orders Contract",
            "description": "Contract for the orders domain",
            "owner": "data-engineering",
            "status": "draft",
            "tags": [],
        },
        "tables": [],   # list of table dicts built in Schema Builder
        "validation_result": None,
        "saved_contracts": [],
        "active_contract_file": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sync_yaml_from_builder():
    """Rebuild YAML from schema builder state."""
    from utils.builder import build_yaml_from_state
    st.session_state["yaml_content"] = build_yaml_from_state()


def sync_builder_from_yaml():
    """Parse YAML into schema builder state."""
    from utils.parser import parse_yaml_to_state
    parse_yaml_to_state(st.session_state["yaml_content"])
