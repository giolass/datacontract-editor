"""Build YAML from all section states — Source Data Contract ODCS v3.1.0."""
import streamlit as st
import yaml


def _clean(d):
    return {k: v for k, v in d.items() if v not in ("", None, [], {})}


def build_yaml_from_state() -> str:
    f   = st.session_state.get("fundamentals", {})
    svs = st.session_state.get("servers", [])
    tbs = st.session_state.get("tables", [])
    qrs = st.session_state.get("quality_rules", [])
    dqx = st.session_state.get("dqx_checks", {})
    tm  = st.session_state.get("team", [])
    sl  = st.session_state.get("sla", [])
    cp  = st.session_state.get("custom_props", [])

    doc = {
        "kind":       f.get("kind", "DataContract"),
        "apiVersion": f.get("apiVersion", "v3.1.0"),
        "id":         f.get("id", ""),
        "name":       f.get("name", ""),
        "version":    f.get("version", "1.0.0"),
        "status":     f.get("status", "draft"),
        "domain":     f.get("domain", ""),
    }
    if f.get("dataProduct"): doc["dataProduct"] = f["dataProduct"]
    if f.get("tenant"):      doc["tenant"]      = f["tenant"]

    desc = _clean({"purpose": f.get("purpose",""), "limitations": f.get("limitations",""), "usage": f.get("usage","")})
    if desc: doc["description"] = desc

    auth_defs = [_clean({"type": a["type"], "url": a["url"], "description": a.get("description","")})
                 for a in f.get("authDefs", []) if a.get("url")]
    if auth_defs: doc["authoritativeDefinitions"] = auth_defs

    tags = f.get("tags", [])
    if tags: doc["tags"] = tags

    # ── Servers ────────────────────────────────────────────────────────────────
    servers_list = []
    for s in svs:
        if not s.get("server","").strip(): continue
        sdef = _clean({
            "server":      s.get("server",""),
            "type":        s.get("type","oracle"),
            "environment": s.get("environment","production"),
            "host":        s.get("host",""),
            "port":        int(s["port"]) if str(s.get("port","")).isdigit() else None,
            "database":    s.get("database",""),
            "schema":      s.get("schema",""),
            "catalog":     s.get("catalog",""),
            "project":     s.get("project",""),
            "dataset":     s.get("dataset",""),
            "account":     s.get("account",""),
            "warehouse":   s.get("warehouse",""),
            "location":    s.get("location",""),
            "path":        s.get("path",""),
            "description": s.get("description",""),
        })
        srv_roles = s.get("roles",[])
        if srv_roles: sdef["roles"] = srv_roles
        servers_list.append(sdef)
    if servers_list: doc["servers"] = servers_list

    # ── Schema ─────────────────────────────────────────────────────────────────
    schema_list = []
    for t in tbs:
        if not t.get("name","").strip(): continue
        props = []
        for p in t.get("properties", []):
            if not p.get("name","").strip(): continue
            pdef = _clean({
                "name":            p["name"],
                "businessName":    p.get("businessName",""),
                "physicalType":    p.get("physicalType",""),
                "primaryKey":      True if p.get("primaryKey") else None,
                "primaryKeyPosition": p.get("primaryKeyPosition") if p.get("primaryKey") else None,
                "required":        True if p.get("required") else None,
                "unique":          True if p.get("unique") else None,
                "description":     p.get("description",""),
                "classification":  p.get("classification",""),
            })
            # logical type options
            opts = {}
            if p.get("lto_enum"): opts["enum"] = [v.strip() for v in p["lto_enum"].split(",") if v.strip()]
            if p.get("lto_min") not in ("",None): opts["minimum"] = p["lto_min"]
            if p.get("lto_max") not in ("",None): opts["maximum"] = p["lto_max"]
            if opts: pdef["logicalTypeOptions"] = opts
            # examples
            if p.get("examples"):
                pdef["examples"] = [v.strip() for v in str(p["examples"]).split(",") if v.strip()]
            # tags
            tags_raw = p.get("tags","")
            if tags_raw:
                pdef["tags"] = [v.strip() for v in tags_raw.split(",") if v.strip()]
            props.append(pdef)

        tdef = _clean({
            "name":         t["name"],
            "physicalName": t.get("physicalName",""),
            "physicalType": t.get("physicalType","TABLE"),
            "description":  t.get("description",""),
        })
        if t.get("tags"):
            tdef["tags"] = [v.strip() for v in t["tags"].split(",") if v.strip()]
        if props: tdef["properties"] = props
        schema_list.append(tdef)
    if schema_list: doc["schema"] = schema_list

    # ── Quality rules (ODCS declarative) ──────────────────────────────────────
    q_list = []
    for r in qrs:
        if not r.get("rule","").strip(): continue
        rdef = _clean({
            "rule":           r["rule"],
            "description":    r.get("description",""),
            "dimension":      r.get("dimension","completeness"),
            "type":           "library",
            "severity":       r.get("severity","error"),
            "businessImpact": r.get("driver","operational"),
            "element":        r.get("element",""),
        })
        if r.get("schedule"): rdef["schedule"] = r["schedule"]; rdef["scheduler"] = "cron"
        q_list.append(rdef)
    if q_list: doc["quality"] = q_list

    # ── DQX checks ─────────────────────────────────────────────────────────────
    dqx_out = {}
    for tname, checks in dqx.items():
        if not tname or not checks: continue
        valid = []
        for c in checks:
            if not c.get("function","").strip(): continue
            args = {}
            col = c.get("column","").strip()
            if col: args["column"] = col
            # extra args from free text
            extra_raw = c.get("extra_args","").strip()
            if extra_raw:
                try:
                    import json
                    extra = json.loads(extra_raw)
                    args.update(extra)
                except Exception:
                    pass
            check_def = {"function": c["function"]}
            if args: check_def["arguments"] = args
            entry = _clean({"criticality": c.get("criticality","error"), "name": c.get("name",""), "check": check_def})
            valid.append(entry)
        if valid: dqx_out[tname] = valid
    if dqx_out: doc["dqx_checks"] = dqx_out

    # ── Team ───────────────────────────────────────────────────────────────────
    team_list = [_clean({"username": m.get("username",""), "name": m.get("name",""),
                          "email": m.get("email",""), "role": m.get("role","owner"),
                          "dateIn": m.get("dateIn","")})
                 for m in tm if m.get("name") or m.get("username")]
    if team_list: doc["team"] = team_list

    # ── SLA ────────────────────────────────────────────────────────────────────
    sla_list = []
    for s in sl:
        if not s.get("property","").strip(): continue
        sdef = _clean({
            "property":    s["property"],
            "value":       _try_num(s.get("value","")),
            "unit":        s.get("unit",""),
            "driver":      s.get("driver","operational"),
            "description": s.get("description",""),
            "element":     s.get("element",""),
            "schedule":    s.get("schedule",""),
            "scheduler":   "cron" if s.get("schedule","") else None,
        })
        sla_list.append(sdef)
    if sla_list: doc["slaProperties"] = sla_list

    # ── Custom properties ──────────────────────────────────────────────────────
    cp_list = [_clean({"property": p.get("property",""), "value": p.get("value","")})
               for p in cp if p.get("property","").strip()]
    if cp_list: doc["customProperties"] = cp_list

    return yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _try_num(v):
    try: return int(v)
    except (ValueError, TypeError): pass
    try: return float(v)
    except (ValueError, TypeError): pass
    return v
