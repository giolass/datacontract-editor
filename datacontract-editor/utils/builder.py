"""Build YAML string from session state (Schema Builder → YAML)."""
import streamlit as st
import yaml


def build_yaml_from_state() -> str:
    meta = st.session_state.get("contract_meta", {})
    tables = st.session_state.get("tables", [])

    contract = {
        "dataContractSpecification": "1.1.0",
        "id": meta.get("id", "urn:datacontract:com:example:new"),
        "info": {
            "title": meta.get("title", "New Contract"),
            "version": meta.get("version", "1.0.0"),
            "description": meta.get("description", ""),
            "owner": meta.get("owner", ""),
            "status": meta.get("status", "draft"),
        },
        "models": {},
    }

    tags = meta.get("tags", [])
    if tags:
        contract["info"]["tags"] = tags

    for table in tables:
        tname = table.get("name", "").strip()
        if not tname:
            continue
        fields = {}
        for f in table.get("fields", []):
            fname = f.get("name", "").strip()
            if not fname:
                continue
            fdef = {"type": f.get("type", "string")}
            if f.get("required"):
                fdef["required"] = True
            if f.get("unique"):
                fdef["unique"] = True
            if f.get("pii"):
                fdef["pii"] = True
            if f.get("description"):
                fdef["description"] = f["description"]
            if f.get("example"):
                fdef["example"] = f["example"]
            if f.get("enum_values"):
                raw = f["enum_values"]
                vals = [v.strip() for v in raw.split(",") if v.strip()]
                if vals:
                    fdef["enum"] = vals
            fields[fname] = fdef
        contract["models"][tname] = {
            "description": table.get("description", ""),
            "type": "table",
            "fields": fields,
        }

    return yaml.dump(contract, allow_unicode=True, sort_keys=False, default_flow_style=False)
