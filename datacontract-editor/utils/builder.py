"""Build unified YAML from all section states."""
import streamlit as st
import yaml


def _clean(d: dict) -> dict:
    """Remove empty string values from dict."""
    return {k: v for k, v in d.items() if v not in ("", None, [], {})}


def build_yaml_from_state() -> str:
    f  = st.session_state.get("fundamentals", {})
    t  = st.session_state.get("terms", {})
    tm = st.session_state.get("team", {})
    sv = st.session_state.get("servers", [])
    rl = st.session_state.get("roles", [])
    sp = st.session_state.get("support", {})
    pr = st.session_state.get("pricing", {})
    sl = st.session_state.get("sla", {})
    tb = st.session_state.get("tables", [])

    # ── info block ────────────────────────────────────────────────────────────
    info = _clean({
        "title":       f.get("title", ""),
        "version":     f.get("version", "1.0.0"),
        "status":      f.get("status", "draft"),
        "description": f.get("description", ""),
        "owner":       tm.get("owner", ""),
        "ownerEmail":  tm.get("ownerEmail", ""),
        "dataProduct": tm.get("dataProduct", ""),
        "domain":      tm.get("domain", ""),
    })

    contacts = tm.get("contacts", [])
    if contacts:
        info["contact"] = [_clean(c) for c in contacts if c.get("name") or c.get("email")]

    tags = f.get("tags", [])
    if tags:
        info["tags"] = tags

    # ── servers ───────────────────────────────────────────────────────────────
    servers_block = {}
    for s in sv:
        name = s.get("name", "").strip()
        if not name:
            continue
        sdef = _clean({
            "type":        s.get("type", "databricks"),
            "environment": s.get("environment", ""),
            "description": s.get("description", ""),
            "catalog":     s.get("catalog", ""),
            "schema":      s.get("schema", ""),
            "database":    s.get("database", ""),
            "host":        s.get("host", ""),
            "port":        s.get("port", ""),
            "project":     s.get("project", ""),
            "dataset":     s.get("dataset", ""),
            "account":     s.get("account", ""),
            "warehouse":   s.get("warehouse", ""),
            "path":        s.get("path", ""),
            "location":    s.get("location", ""),
        })
        srv_roles = s.get("roles", [])
        if srv_roles:
            sdef["roles"] = srv_roles
        servers_block[name] = sdef

    # ── models ────────────────────────────────────────────────────────────────
    models_block = {}
    for table in tb:
        tname = table.get("name", "").strip()
        if not tname:
            continue
        fields = {}
        for field in table.get("fields", []):
            fname = field.get("name", "").strip()
            if not fname:
                continue
            fdef = {"type": field.get("type", "string")}
            if field.get("required"):   fdef["required"]    = True
            if field.get("unique"):     fdef["unique"]      = True
            if field.get("pii"):        fdef["pii"]         = True
            if field.get("nullable") is False: fdef["nullable"] = False
            if field.get("description"): fdef["description"] = field["description"]
            if field.get("example"):    fdef["example"]     = field["example"]
            if field.get("tags"):
                raw = field["tags"]
                vals = [v.strip() for v in raw.split(",") if v.strip()]
                if vals: fdef["tags"] = vals
            enum_raw = field.get("enum_values", "")
            if enum_raw:
                vals = [v.strip() for v in enum_raw.split(",") if v.strip()]
                if vals: fdef["enum"] = vals
            fields[fname] = fdef
        models_block[tname] = _clean({
            "description": table.get("description", ""),
            "type":        "table",
            "tags":        [t.strip() for t in table.get("tags","").split(",") if t.strip()] or None,
            "fields":      fields,
        })
        if not models_block[tname].get("tags"):
            models_block[tname].pop("tags", None)

    # ── roles ─────────────────────────────────────────────────────────────────
    roles_block = [
        _clean({"role": r.get("name",""), "access": r.get("access",""), "description": r.get("description","")})
        for r in rl if r.get("name")
    ]

    # ── terms ─────────────────────────────────────────────────────────────────
    terms_block = _clean({
        "usage":        t.get("usage", ""),
        "limitations":  t.get("limitations", ""),
        "billing":      t.get("billing", ""),
        "noticePeriod": t.get("noticePeriod", ""),
    })

    # ── support ───────────────────────────────────────────────────────────────
    support_block = _clean({
        "channel":       sp.get("channel", ""),
        "url":           sp.get("url", ""),
        "on_call":       sp.get("on_call", ""),
        "documentation": sp.get("doc_url", ""),
    })

    # ── pricing ───────────────────────────────────────────────────────────────
    pricing_block = _clean({
        "billing":   pr.get("billing", ""),
        "amount":    pr.get("price_amount", ""),
        "currency":  pr.get("price_currency", ""),
        "unit":      pr.get("price_unit", ""),
    })

    # ── SLA ───────────────────────────────────────────────────────────────────
    sla_block = {}
    if sl.get("availability"):
        sla_block["availability"] = {"description": "Percentage of time data is available", "percentage": sl["availability"]}
    if sl.get("freshness_threshold"):
        sla_block["freshness"] = _clean({"description": sl.get("freshness_description",""), "threshold": sl["freshness_threshold"]})
    if sl.get("retention"):
        sla_block["retention"] = {"description": "Data retention period", "period": sl["retention"]}
    if sl.get("latency"):
        sla_block["latency"] = {"description": "Query response time", "threshold": sl["latency"]}
    if sl.get("support_time") or sl.get("support_response"):
        sla_block["support"] = _clean({"time": sl.get("support_time",""), "responseTime": sl.get("support_response","")})
    if sl.get("backup_time") or sl.get("backup_recovery"):
        sla_block["backup"] = _clean({"time": sl.get("backup_time",""), "recoveryTime": sl.get("backup_recovery","")})

    # ── assemble ──────────────────────────────────────────────────────────────
    contract = {"dataContractSpecification": "1.1.0", "id": f.get("id",""), "info": info}
    if servers_block:  contract["servers"]      = servers_block
    if terms_block:    contract["terms"]        = terms_block
    if models_block:   contract["models"]       = models_block
    if roles_block:    contract["roles"]        = roles_block
    if support_block:  contract["support"]      = support_block
    if pricing_block:  contract["pricing"]      = pricing_block
    if sla_block:      contract["servicelevels"]= sla_block

    return yaml.dump(contract, allow_unicode=True, sort_keys=False, default_flow_style=False)
