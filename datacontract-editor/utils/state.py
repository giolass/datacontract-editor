"""Session state initialization — all sections feed one unified YAML."""
import streamlit as st
from utils.templates import DEFAULT_CONTRACT


def init_session_state():
    defaults = {
        # ── Active section in left nav ────────────────────────────────────────
        "active_section": "fundamentals",

        # ── Unified YAML output ───────────────────────────────────────────────
        "yaml_content": DEFAULT_CONTRACT,

        # ── Section: Fundamentals ─────────────────────────────────────────────
        "fundamentals": {
            "id": "urn:datacontract:bpt:example:orders",
            "title": "Orders Data Contract",
            "version": "1.0.0",
            "status": "draft",
            "description": "",
            "tags": [],
        },

        # ── Section: Terms of Use ─────────────────────────────────────────────
        "terms": {
            "usage": "",
            "limitations": "",
            "billing": "Free",
            "noticePeriod": "P3M",
        },

        # ── Section: Schemas (tables + fields) ───────────────────────────────
        "tables": [],

        # ── Section: Servers / Environments ──────────────────────────────────
        "servers": [],

        # ── Section: Team / Owners ────────────────────────────────────────────
        "team": {
            "owner": "",
            "ownerEmail": "",
            "dataProduct": "",
            "domain": "",
            "contacts": [],   # [{name, email, role}]
        },

        # ── Section: Support ──────────────────────────────────────────────────
        "support": {
            "channel": "",
            "url": "",
            "on_call": "",
            "doc_url": "",
        },

        # ── Section: Roles ────────────────────────────────────────────────────
        "roles": [],   # [{name, access, description}]

        # ── Section: Pricing ─────────────────────────────────────────────────
        "pricing": {
            "billing": "Free",
            "price_amount": "",
            "price_currency": "USD",
            "price_unit": "per month",
        },

        # ── Section: SLA ──────────────────────────────────────────────────────
        "sla": {
            "availability": "99.9%",
            "freshness_threshold": "1h",
            "freshness_description": "",
            "retention": "1 year",
            "latency": "",
            "support_time": "9x5",
            "support_response": "1h",
            "backup_time": "",
            "backup_recovery": "",
        },

        # ── UI state ──────────────────────────────────────────────────────────
        "validation_result": None,
        "active_contract_file": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sync_yaml():
    """Rebuild the unified YAML from ALL section states."""
    from utils.builder import build_yaml_from_state
    st.session_state["yaml_content"] = build_yaml_from_state()


def parse_yaml():
    """Parse YAML back into all section states."""
    from utils.parser import parse_yaml_to_state
    parse_yaml_to_state(st.session_state["yaml_content"])
