import streamlit as st, uuid
from utils.templates import LOGICAL_TYPES, PHYSICAL_TYPES_MAP, CLASSIFICATION
from utils.state import sync_yaml


def _uid(): return str(uuid.uuid4())[:8]

def _new_prop():
    return {"id": _uid(), "name": "", "businessName": "", "logicalType": "string",
            "physicalType": "", "primaryKey": False, "required": False, "unique": False,
            "criticalDataElement": False, "description": "", "classification": "",
            "examples": "", "tags": "", "lto_enum": "", "lto_min": "", "lto_max": "", "lto_format": ""}

def _new_table():
    return {"id": _uid(), "name": "", "physicalName": "", "physicalType": "TABLE",
            "description": "", "tags": "", "properties": [_new_prop()]}


def render():
    st.markdown('<div class="section-header">🗄️ Schema</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Modelo físico y lógico de los datos: tablas, columnas, tipos, restricciones y clasificación.</div>', unsafe_allow_html=True)

    tables = st.session_state["tables"]
    # Detect server type for physical type hints
    svs = st.session_state.get("servers", [])
    stype = svs[0].get("type","oracle") if svs else "oracle"
    phys_hints = PHYSICAL_TYPES_MAP.get(stype, PHYSICAL_TYPES_MAP["default"])

    if not tables:
        st.info("Sin tablas definidas. Haz clic en **＋ Add Table**.")

    for t_idx, table in enumerate(tables):
        tid = table.get("id", str(t_idx))
        n_props = len(table.get("properties",[]))
        label = f"📊  **{table['name'] or '(sin nombre)'}** · {table.get('physicalName','')} · {n_props} column{'s' if n_props!=1 else ''}"

        with st.expander(label, expanded=t_idx == 0):
            # Table header
            tc1, tc2, tc3, tc4, tc_del = st.columns([2, 3, 2, 2, 1])
            with tc1:
                v = st.text_input("Table name *", value=table["name"], key=f"tn_{tid}", placeholder="orders")
                if v != table["name"]: table["name"] = v; sync_yaml()
            with tc2:
                v = st.text_input("Physical name", value=table.get("physicalName",""), key=f"tpn_{tid}", placeholder="SCHEMA.TABLE_NAME")
                if v != table.get("physicalName"): table["physicalName"] = v; sync_yaml()
            with tc3:
                pt_opts = ["TABLE","VIEW","MATERIALIZED VIEW","EXTERNAL TABLE","SYNONYM"]
                idx = pt_opts.index(table.get("physicalType","TABLE")) if table.get("physicalType") in pt_opts else 0
                v = st.selectbox("Physical type", pt_opts, index=idx, key=f"tpt_{tid}")
                if v != table.get("physicalType"): table["physicalType"] = v; sync_yaml()
            with tc4:
                v = st.text_input("Tags", value=table.get("tags",""), key=f"ttag_{tid}", placeholder="fact-table, critical")
                if v != table.get("tags"): table["tags"] = v; sync_yaml()
            with tc_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"tdel_{tid}"):
                    tables.pop(t_idx); sync_yaml(); st.rerun()

            v = st.text_area("Description", value=table.get("description",""), height=55, key=f"tdesc_{tid}", placeholder="What does this table contain?")
            if v != table.get("description"): table["description"] = v; sync_yaml()

            # Properties header
            st.markdown('<div class="fields-header">Properties / Columns</div>', unsafe_allow_html=True)
            hcols = st.columns([3, 2.5, 2.5, 1, 1, 1, 1, 3, 3, 1])
            for hc, hl in zip(hcols, ["Name *","Logical Type","Physical Type","PK","Req","Uniq","CDE","Description","Class / Examples / Tags",""]):
                hc.markdown(f'<div class="field-col-hdr">{hl}</div>', unsafe_allow_html=True)

            for f_idx, prop in enumerate(table.get("properties",[])):
                pid = prop.get("id", str(f_idx))
                pc = st.columns([3, 2.5, 2.5, 1, 1, 1, 1, 3, 3, 1])

                with pc[0]:
                    v = st.text_input("", value=prop["name"], key=f"pn_{tid}_{pid}", placeholder="column_name", label_visibility="collapsed")
                    if v != prop["name"]: prop["name"] = v; sync_yaml()
                with pc[1]:
                    idx = LOGICAL_TYPES.index(prop.get("logicalType","string")) if prop.get("logicalType") in LOGICAL_TYPES else 0
                    v = st.selectbox("", LOGICAL_TYPES, index=idx, key=f"plt_{tid}_{pid}", label_visibility="collapsed")
                    if v != prop.get("logicalType"): prop["logicalType"] = v; sync_yaml()
                with pc[2]:
                    v = st.text_input("", value=prop.get("physicalType",""), key=f"ppt_{tid}_{pid}",
                                      placeholder=phys_hints[0] if phys_hints else "VARCHAR2(n)", label_visibility="collapsed")
                    if v != prop.get("physicalType"): prop["physicalType"] = v; sync_yaml()
                for pci, pkey in [(3,"primaryKey"),(4,"required"),(5,"unique"),(6,"criticalDataElement")]:
                    with pc[pci]:
                        v = st.checkbox("", value=bool(prop.get(pkey,False)), key=f"p{pkey}_{tid}_{pid}", label_visibility="collapsed")
                        if v != prop.get(pkey): prop[pkey] = v; sync_yaml()
                with pc[7]:
                    v = st.text_input("", value=prop.get("description",""), key=f"pdesc_{tid}_{pid}",
                                      placeholder="Column description", label_visibility="collapsed")
                    if v != prop.get("description"): prop["description"] = v; sync_yaml()
                with pc[8]:
                    # classification + examples in one field (tab-separated display)
                    cls_opts = [""] + CLASSIFICATION
                    idx = cls_opts.index(prop.get("classification","")) if prop.get("classification") in cls_opts else 0
                    v = st.selectbox("", cls_opts, index=idx, key=f"pcls_{tid}_{pid}", label_visibility="collapsed")
                    if v != prop.get("classification"): prop["classification"] = v; sync_yaml()
                with pc[9]:
                    if st.button("✕", key=f"pdel_{tid}_{pid}"):
                        table["properties"].pop(f_idx); sync_yaml(); st.rerun()

                # Expanded details (tags, examples, enum, min/max)
                with st.expander(f"⚙ {prop['name'] or 'column'} — details", expanded=False):
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        v = st.text_input("Business Name", value=prop.get("businessName",""), key=f"pbn_{tid}_{pid}")
                        if v != prop.get("businessName"): prop["businessName"] = v; sync_yaml()
                    with d2:
                        v = st.text_input("Examples", value=prop.get("examples",""), key=f"pex_{tid}_{pid}", placeholder="val1, val2")
                        if v != prop.get("examples"): prop["examples"] = v; sync_yaml()
                    with d3:
                        v = st.text_input("Tags", value=prop.get("tags",""), key=f"ptag_{tid}_{pid}", placeholder="pk, pii, fk:table")
                        if v != prop.get("tags"): prop["tags"] = v; sync_yaml()
                    e1, e2, e3, e4 = st.columns(4)
                    with e1:
                        v = st.text_input("Enum values", value=prop.get("lto_enum",""), key=f"penum_{tid}_{pid}", placeholder="val1, val2, val3")
                        if v != prop.get("lto_enum"): prop["lto_enum"] = v; sync_yaml()
                    with e2:
                        v = st.text_input("Min", value=str(prop.get("lto_min","")), key=f"pmin_{tid}_{pid}")
                        if v != str(prop.get("lto_min","")): prop["lto_min"] = v; sync_yaml()
                    with e3:
                        v = st.text_input("Max", value=str(prop.get("lto_max","")), key=f"pmax_{tid}_{pid}")
                        if v != str(prop.get("lto_max","")): prop["lto_max"] = v; sync_yaml()
                    with e4:
                        v = st.text_input("Format", value=prop.get("lto_format",""), key=f"pfmt_{tid}_{pid}", placeholder="uuid, email, url")
                        if v != prop.get("lto_format"): prop["lto_format"] = v; sync_yaml()

            if st.button("＋ Add Column", key=f"add_prop_{tid}"):
                table["properties"].append(_new_prop()); sync_yaml(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Table", type="primary", key="btn_add_table"):
        tables.append(_new_table()); sync_yaml(); st.rerun()
