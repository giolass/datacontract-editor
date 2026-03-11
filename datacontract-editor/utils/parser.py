"""Parse YAML → all section states."""
import streamlit as st
import yaml


def parse_yaml_to_state(yaml_str: str):
    try:
        doc = yaml.safe_load(yaml_str) or {}
    except Exception:
        return

    info = doc.get("info", {}) or {}
    terms = doc.get("terms", {}) or {}
    models = doc.get("models", {}) or {}
    servers_raw = doc.get("servers", {}) or {}
    roles_raw = doc.get("roles", []) or []
    support_raw = doc.get("support", {}) or {}
    pricing_raw = doc.get("pricing", {}) or {}
    sla_raw = doc.get("servicelevels", {}) or {}

    # fundamentals
    st.session_state["fundamentals"] = {
        "id":          doc.get("id", ""),
        "title":       info.get("title", ""),
        "version":     info.get("version", "1.0.0"),
        "status":      info.get("status", "draft"),
        "description": info.get("description", ""),
        "tags":        info.get("tags", []),
    }

    # team
    contacts_raw = info.get("contact", []) or []
    if isinstance(contacts_raw, dict):
        contacts_raw = [contacts_raw]
    st.session_state["team"] = {
        "owner":       info.get("owner", ""),
        "ownerEmail":  info.get("ownerEmail", ""),
        "dataProduct": info.get("dataProduct", ""),
        "domain":      info.get("domain", ""),
        "contacts":    [{"name": c.get("name",""), "email": c.get("email",""), "role": c.get("role","")} for c in contacts_raw],
    }

    # terms
    st.session_state["terms"] = {
        "usage":        terms.get("usage", ""),
        "limitations":  terms.get("limitations", ""),
        "billing":      terms.get("billing", "Free"),
        "noticePeriod": terms.get("noticePeriod", "P3M"),
    }

    # servers
    svs = []
    for sname, sdef in (servers_raw.items() if isinstance(servers_raw, dict) else []):
        if not isinstance(sdef, dict):
            continue
        svs.append({
            "name":        sname,
            "type":        sdef.get("type", "databricks"),
            "environment": sdef.get("environment", ""),
            "description": sdef.get("description", ""),
            "catalog":     sdef.get("catalog", ""),
            "schema":      sdef.get("schema", ""),
            "database":    sdef.get("database", ""),
            "host":        sdef.get("host", ""),
            "port":        str(sdef.get("port", "")),
            "project":     sdef.get("project", ""),
            "dataset":     sdef.get("dataset", ""),
            "account":     sdef.get("account", ""),
            "warehouse":   sdef.get("warehouse", ""),
            "path":        sdef.get("path", ""),
            "location":    sdef.get("location", ""),
            "roles":       sdef.get("roles", []),
        })
    st.session_state["servers"] = svs

    # tables / schemas
    tables = []
    import uuid
    for tname, tdef in models.items():
        if not isinstance(tdef, dict):
            continue
        raw_fields = tdef.get("fields", {}) or {}
        fields = []
        for fname, fdef in raw_fields.items():
            if not isinstance(fdef, dict):
                fdef = {}
            fields.append({
                "id":          str(uuid.uuid4())[:8],
                "name":        fname,
                "type":        fdef.get("type", "string"),
                "required":    fdef.get("required", False),
                "unique":      fdef.get("unique", False),
                "pii":         fdef.get("pii", False),
                "nullable":    fdef.get("nullable", True),
                "description": fdef.get("description", ""),
                "example":     str(fdef.get("example", "")),
                "tags":        ", ".join(fdef.get("tags", [])),
                "enum_values": ", ".join(str(v) for v in fdef.get("enum", [])),
            })
        tables.append({
            "id":          str(uuid.uuid4())[:8],
            "name":        tname,
            "description": tdef.get("description", ""),
            "tags":        ", ".join(tdef.get("tags", [])) if isinstance(tdef.get("tags"), list) else "",
            "fields":      fields,
        })
    st.session_state["tables"] = tables

    # roles
    roles = []
    for r in (roles_raw if isinstance(roles_raw, list) else []):
        if isinstance(r, dict):
            roles.append({"name": r.get("role",""), "access": r.get("access",""), "description": r.get("description","")})
    st.session_state["roles"] = roles

    # support
    st.session_state["support"] = {
        "channel": support_raw.get("channel", ""),
        "url":     support_raw.get("url", ""),
        "on_call": support_raw.get("on_call", ""),
        "doc_url": support_raw.get("documentation", ""),
    }

    # pricing
    st.session_state["pricing"] = {
        "billing":        pricing_raw.get("billing", "Free"),
        "price_amount":   str(pricing_raw.get("amount", "")),
        "price_currency": pricing_raw.get("currency", "USD"),
        "price_unit":     pricing_raw.get("unit", "per month"),
    }

    # sla
    avail = sla_raw.get("availability", {}) or {}
    fresh = sla_raw.get("freshness", {}) or {}
    ret   = sla_raw.get("retention", {}) or {}
    lat   = sla_raw.get("latency", {}) or {}
    sup   = sla_raw.get("support", {}) or {}
    bkp   = sla_raw.get("backup", {}) or {}
    st.session_state["sla"] = {
        "availability":           avail.get("percentage", "99.9%"),
        "freshness_threshold":    fresh.get("threshold", "1h"),
        "freshness_description":  fresh.get("description", ""),
        "retention":              ret.get("period", "1 year"),
        "latency":                lat.get("threshold", ""),
        "support_time":           sup.get("time", "9x5"),
        "support_response":       sup.get("responseTime", "1h"),
        "backup_time":            bkp.get("time", ""),
        "backup_recovery":        bkp.get("recoveryTime", ""),
    }
