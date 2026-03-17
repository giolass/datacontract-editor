"""Session state — Source Data Contract (ODCS v3.1.0)."""
import streamlit as st
from utils.templates import DEFAULT_CONTRACT
import uuid


def _uid(): return str(uuid.uuid4())[:8]


def init_session_state():
    defaults = {
        "active_section":       "fundamentals",
        "yaml_content":         DEFAULT_CONTRACT,
        "validation_result":    None,
        "active_contract_file": None,

        # ── Fundamentals ──────────────────────────────────────────────────────
        "fundamentals": {
            "kind": "DataContract", "apiVersion": "v3.1.0",
            "id": "urn:datacontract:bpt:domain:source-name",
            "name": "", "version": "1.0.0", "status": "draft",
            "domain": "", "dataProduct": "", "tenant": "BPT",
            "purpose": "", "limitations": "", "usage": "",
            "tags": [],
            "authDefs": [],   # [{type, url, description}]
        },

        # ── Servers ───────────────────────────────────────────────────────────
        "servers": [],

        # ── Schema (tables + properties) ──────────────────────────────────────
        "tables": [],

        # ── Quality ODCS (declarative rules) ─────────────────────────────────
        "quality_rules": [],

        # ── DQX Checks (executable Spark checks) ─────────────────────────────
        "dqx_checks": {},   # {table_name: [{criticality, name, function, args}]}

        # ── Team ──────────────────────────────────────────────────────────────
        "team": [],

        # ── SLA ───────────────────────────────────────────────────────────────
        "sla": [
            {"id": _uid(), "property": "availability", "value": "99.5", "unit": "percent", "driver": "operational", "description": "", "element": ""},
            {"id": _uid(), "property": "freshness",    "value": "1",    "unit": "h",       "driver": "analytics",  "description": "", "element": ""},
            {"id": _uid(), "property": "retention",    "value": "1",    "unit": "year",    "driver": "regulatory", "description": "", "element": ""},
            {"id": _uid(), "property": "frequency",    "value": "daily","unit": "",        "driver": "operational","description": "Carga batch diaria", "element": "", "schedule": "0 1 * * *"},
        ],

        # ── Custom Properties ─────────────────────────────────────────────────
        "custom_props": [
            {"id": _uid(), "property": "databricksCatalog",     "value": ""},
            {"id": _uid(), "property": "databricksSchema",      "value": ""},
            {"id": _uid(), "property": "databricksTargetTable", "value": ""},
            {"id": _uid(), "property": "ingestionTool",         "value": "Apache Spark / Databricks Jobs"},
            {"id": _uid(), "property": "sourceSystem",          "value": ""},
            {"id": _uid(), "property": "encryptionRequired",    "value": "true"},
        ],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sync_yaml():
    from utils.builder import build_yaml_from_state
    st.session_state["yaml_content"] = build_yaml_from_state()


def parse_yaml():
    from utils.parser import parse_yaml_to_state
    parse_yaml_to_state(st.session_state["yaml_content"])
