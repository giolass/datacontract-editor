"""Parse YAML → session state — Source Data Contract ODCS v3.1.0."""
import streamlit as st
import yaml, uuid


def _uid(): return str(uuid.uuid4())[:8]


def parse_yaml_to_state(yaml_str: str):
    try:
        doc = yaml.safe_load(yaml_str) or {}
    except Exception:
        return

    desc = doc.get("description", {}) or {}
    if isinstance(desc, str): desc = {"purpose": desc}

    auth_defs_raw = doc.get("authoritativeDefinitions", []) or []

    st.session_state["fundamentals"] = {
        "kind":        doc.get("kind", "DataContract"),
        "apiVersion":  doc.get("apiVersion", "v3.1.0"),
        "id":          doc.get("id", ""),
        "name":        doc.get("name", ""),
        "version":     doc.get("version", "1.0.0"),
        "status":      doc.get("status", "draft"),
        "domain":      doc.get("domain", ""),
        "dataProduct": doc.get("dataProduct", ""),
        "tenant":      doc.get("tenant", "BPT"),
        "purpose":     desc.get("purpose", ""),
        "limitations": desc.get("limitations", ""),
        "usage":       desc.get("usage", ""),
        "tags":        doc.get("tags", []),
        "authDefs":    [{"id": _uid(), "type": a.get("type",""), "url": a.get("url",""), "description": a.get("description","")}
                        for a in auth_defs_raw if isinstance(a, dict)],
    }

    # Servers
    svs = []
    for s in (doc.get("servers", []) or []):
        if not isinstance(s, dict): continue
        svs.append({
            "id": _uid(), "server": s.get("server",""),
            "type": s.get("type","oracle"), "environment": s.get("environment","production"),
            "host": s.get("host",""), "port": str(s.get("port","")),
            "database": s.get("database",""), "schema": s.get("schema",""),
            "catalog": s.get("catalog",""), "project": s.get("project",""),
            "dataset": s.get("dataset",""), "account": s.get("account",""),
            "warehouse": s.get("warehouse",""), "location": s.get("location",""),
            "path": s.get("path",""), "description": s.get("description",""),
            "roles": s.get("roles", []),
        })
    st.session_state["servers"] = svs

    # Schema → tables
    tables = []
    for t in (doc.get("schema", []) or []):
        if not isinstance(t, dict): continue
        props = []
        for p in (t.get("properties", []) or []):
            if not isinstance(p, dict): continue
            lto = p.get("logicalTypeOptions", {}) or {}
            tags_raw = p.get("tags", [])
            tags_str = ", ".join(str(x) for x in tags_raw) if isinstance(tags_raw, list) else str(tags_raw)
            ex_raw = p.get("examples", [])
            examples_str = ", ".join(str(x) for x in ex_raw) if isinstance(ex_raw, list) else str(ex_raw or "")
            props.append({
                "id": _uid(),
                "name": p.get("name",""), "businessName": p.get("businessName",""),
                "physicalType": p.get("physicalType",""),
                "primaryKey": bool(p.get("primaryKey")), "primaryKeyPosition": p.get("primaryKeyPosition",""),
                "required": bool(p.get("required")), "unique": bool(p.get("unique")),
                "description": p.get("description",""), "classification": p.get("classification",""),
                "examples": examples_str, "tags": tags_str,
                "lto_enum": ", ".join(str(v) for v in lto.get("enum",[])) if lto.get("enum") else "",
                "lto_min": str(lto.get("minimum","")) if lto.get("minimum") is not None else "",
                "lto_max": str(lto.get("maximum","")) if lto.get("maximum") is not None else "",
            })
        ttags = t.get("tags",[])
        tables.append({
            "id": _uid(), "name": t.get("name",""), "physicalName": t.get("physicalName",""),
            "physicalType": t.get("physicalType","TABLE"), "description": t.get("description",""),
            "tags": ", ".join(ttags) if isinstance(ttags, list) else str(ttags or ""),
            "properties": props,
        })
    st.session_state["tables"] = tables

    # Quality rules
    qrs = []
    for r in (doc.get("quality",[]) or []):
        if not isinstance(r, dict): continue
        qrs.append({
            "id": _uid(), "rule": r.get("rule",""),
            "description": r.get("description",""), "dimension": r.get("dimension","completeness"),
            "severity": r.get("severity","error"),
            "driver": r.get("businessImpact", r.get("driver","operational")),
            "element": r.get("element",""), "schedule": r.get("schedule",""),
        })
    st.session_state["quality_rules"] = qrs

    # DQX checks
    dqx_raw = doc.get("dqx_checks", {}) or {}
    dqx = {}
    for tname, checks in dqx_raw.items():
        parsed = []
        for c in (checks or []):
            if not isinstance(c, dict): continue
            chk = c.get("check", {}) or {}
            args = chk.get("arguments", {}) or {}
            parsed.append({
                "id": _uid(),
                "criticality": c.get("criticality","error"),
                "name": c.get("name",""),
                "function": chk.get("function",""),
                "column": args.get("column",""),
                "extra_args": "",
            })
        dqx[tname] = parsed
    st.session_state["dqx_checks"] = dqx

    # Team
    team = []
    for m in (doc.get("team",[]) or []):
        if not isinstance(m, dict): continue
        team.append({
            "id": _uid(), "username": m.get("username",""), "name": m.get("name",""),
            "email": m.get("email",""), "role": m.get("role","owner"), "dateIn": m.get("dateIn",""),
        })
    st.session_state["team"] = team

    # SLA
    sla = []
    for s in (doc.get("slaProperties",[]) or []):
        if not isinstance(s, dict): continue
        sla.append({
            "id": _uid(), "property": s.get("property",""),
            "value": str(s.get("value","")), "unit": s.get("unit",""),
            "driver": s.get("driver","operational"), "description": s.get("description",""),
            "element": s.get("element",""), "schedule": s.get("schedule",""),
        })
    st.session_state["sla"] = sla

    # Custom props
    cp = []
    for p in (doc.get("customProperties",[]) or []):
        if not isinstance(p, dict): continue
        cp.append({"id": _uid(), "property": p.get("property",""), "value": str(p.get("value",""))})
    st.session_state["custom_props"] = cp
