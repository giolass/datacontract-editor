"""Parse YAML string → session state (YAML Editor → Schema Builder)."""
import streamlit as st
import yaml


def parse_yaml_to_state(yaml_str: str):
    try:
        doc = yaml.safe_load(yaml_str) or {}
    except Exception:
        return

    info = doc.get("info", {})
    st.session_state["contract_meta"] = {
        "id": doc.get("id", ""),
        "version": info.get("version", "1.0.0"),
        "title": info.get("title", ""),
        "description": info.get("description", ""),
        "owner": info.get("owner", ""),
        "status": info.get("status", "draft"),
        "tags": info.get("tags", []),
    }

    models = doc.get("models", {})
    tables = []
    for tname, tdef in (models or {}).items():
        if not isinstance(tdef, dict):
            continue
        raw_fields = tdef.get("fields", {}) or {}
        fields = []
        for fname, fdef in raw_fields.items():
            if not isinstance(fdef, dict):
                fdef = {}
            enum_vals = fdef.get("enum", [])
            fields.append({
                "name": fname,
                "type": fdef.get("type", "string"),
                "required": fdef.get("required", False),
                "unique": fdef.get("unique", False),
                "pii": fdef.get("pii", False),
                "description": fdef.get("description", ""),
                "example": str(fdef.get("example", "")),
                "enum_values": ", ".join(str(v) for v in enum_vals) if enum_vals else "",
            })
        tables.append({
            "name": tname,
            "description": tdef.get("description", ""),
            "fields": fields,
        })
    st.session_state["tables"] = tables
