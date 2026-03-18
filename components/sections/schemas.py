import streamlit as st, uuid
from utils.templates import PHYSICAL_TYPES_MAP, CLASSIFICATION
from utils.state import sync_yaml


def _uid(): return str(uuid.uuid4())[:8]

def _new_prop():
    return {
        "id": _uid(), "name": "", "businessName": "",
        "physicalType": "", "primaryKey": False, "required": False, "unique": False,
        "description": "", "classification": "",
        "examples": "", "tags": "", "lto_enum": "", "lto_min": "", "lto_max": "",
    }

def _new_table():
    return {
        "id": _uid(), "name": "", "physicalName": "", "physicalType": "TABLE",
        "description": "", "tags": "", "properties": [_new_prop()],
    }


def render():
    st.markdown('<div class="section-header">🗄️ Schema</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Modelo físico de los datos: tablas, columnas, tipos y restricciones de la fuente.</div>', unsafe_allow_html=True)

    tables = st.session_state["tables"]

    # Physical type hints based on server type
    svs        = st.session_state.get("servers", [])
    stype      = svs[0].get("type", "oracle") if svs else "oracle"
    phys_hints = PHYSICAL_TYPES_MAP.get(stype, PHYSICAL_TYPES_MAP["default"])
    ph_hint    = phys_hints[0] if phys_hints else "VARCHAR2(n)"

    if not tables:
        st.info("Sin tablas definidas. Haz clic en **＋ Add Table**.")

    for t_idx, table in enumerate(tables):
        tid    = table.get("id", str(t_idx))
        n_cols = len(table.get("properties", []))
        label  = f"📊  **{table['name'] or '(sin nombre)'}** · {table.get('physicalName','')} · {n_cols} column{'s' if n_cols!=1 else ''}"

        with st.expander(label, expanded=t_idx == 0):

            # ── Table metadata ────────────────────────────────────────────────
            tc1, tc2, tc3, tc4, tc_del = st.columns([2, 3, 2, 2, 1])
            with tc1:
                v = st.text_input("Table name *", value=table["name"], key=f"tn_{tid}", placeholder="orders")
                if v != table["name"]: table["name"] = v; sync_yaml()
            with tc2:
                v = st.text_input("Physical name", value=table.get("physicalName",""), key=f"tpn_{tid}", placeholder="SCHEMA.TABLE_NAME")
                if v != table.get("physicalName"): table["physicalName"] = v; sync_yaml()
            with tc3:
                pt_opts = ["TABLE", "VIEW", "MATERIALIZED VIEW", "EXTERNAL TABLE", "SYNONYM"]
                idx = pt_opts.index(table.get("physicalType","TABLE")) if table.get("physicalType") in pt_opts else 0
                v = st.selectbox("Object type", pt_opts, index=idx, key=f"tpt_{tid}")
                if v != table.get("physicalType"): table["physicalType"] = v; sync_yaml()
            with tc4:
                v = st.text_input("Tags", value=table.get("tags",""), key=f"ttag_{tid}", placeholder="fact-table, critical")
                if v != table.get("tags"): table["tags"] = v; sync_yaml()
            with tc_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"tdel_{tid}"):
                    tables.pop(t_idx); sync_yaml(); st.rerun()

            v = st.text_area("Description", value=table.get("description",""), height=60,
                             key=f"tdesc_{tid}", placeholder="What does this table contain?")
            if v != table.get("description"): table["description"] = v; sync_yaml()

            if not table.get("properties"):
                st.caption("Sin columnas. Haz clic en ＋ Add Column.")

            # ── Column header (2 rows of headers to maximize space) ───────────
            st.markdown('<div class="fields-header" style="margin-top:0.75rem">Columns</div>', unsafe_allow_html=True)

            # Row A headers: main fields
            ha = st.columns([3, 3, 1, 1, 1, 1, 1])
            for col, lbl in zip(ha, ["Column Name *", "Physical Type", "PK", "Req", "Uniq", "Class", "Del"]):
                col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

            # Row B headers: extended fields
            hb = st.columns([3, 3, 3, 3])
            for col, lbl in zip(hb, ["Business Name", "Description", "Examples / Enum", "Tags"]):
                col.markdown(f'<div class="field-col-hdr" style="color:var(--gray4)">{lbl}</div>', unsafe_allow_html=True)

            st.markdown('<hr style="margin:0.2rem 0 0.5rem;border-color:var(--border)">', unsafe_allow_html=True)

            # ── Column rows ───────────────────────────────────────────────────
            for f_idx, prop in enumerate(table.get("properties", [])):
                pid = prop.get("id", str(f_idx))

                # — Row A: main fields ————————————————————————————————————————
                ra = st.columns([3, 3, 1, 1, 1, 1, 1])

                with ra[0]:
                    v = st.text_input("", value=prop["name"], key=f"pn_{tid}_{pid}",
                                      placeholder="column_name", label_visibility="collapsed")
                    if v != prop["name"]: prop["name"] = v; sync_yaml()

                with ra[1]:
                    v = st.text_input("", value=prop.get("physicalType",""), key=f"ppt_{tid}_{pid}",
                                      placeholder=ph_hint, label_visibility="collapsed")
                    if v != prop.get("physicalType"): prop["physicalType"] = v; sync_yaml()

                for rci, pkey in [(2,"primaryKey"), (3,"required"), (4,"unique")]:
                    with ra[rci]:
                        v = st.checkbox("", value=bool(prop.get(pkey, False)),
                                        key=f"p{pkey}_{tid}_{pid}", label_visibility="collapsed")
                        if v != prop.get(pkey): prop[pkey] = v; sync_yaml()

                with ra[5]:
                    cls_opts = [""] + CLASSIFICATION
                    idx = cls_opts.index(prop.get("classification","")) if prop.get("classification") in cls_opts else 0
                    v = st.selectbox("", cls_opts, index=idx, key=f"pcls_{tid}_{pid}",
                                     label_visibility="collapsed")
                    if v != prop.get("classification"): prop["classification"] = v; sync_yaml()

                with ra[6]:
                    if st.button("✕", key=f"pdel_{tid}_{pid}"):
                        table["properties"].pop(f_idx); sync_yaml(); st.rerun()

                # — Row B: extended fields (no nested expander) ———————————————
                rb = st.columns([3, 3, 3, 3])

                with rb[0]:
                    v = st.text_input("", value=prop.get("businessName",""), key=f"pbn_{tid}_{pid}",
                                      placeholder="Business name", label_visibility="collapsed")
                    if v != prop.get("businessName"): prop["businessName"] = v; sync_yaml()

                with rb[1]:
                    v = st.text_input("", value=prop.get("description",""), key=f"pdesc_{tid}_{pid}",
                                      placeholder="Description", label_visibility="collapsed")
                    if v != prop.get("description"): prop["description"] = v; sync_yaml()

                with rb[2]:
                    # Examples OR enum values in same field
                    cur = prop.get("lto_enum","") or prop.get("examples","")
                    v = st.text_input("", value=cur, key=f"pex_{tid}_{pid}",
                                      placeholder="val1, val2 / enum values", label_visibility="collapsed")
                    if v != cur:
                        prop["lto_enum"]  = v
                        prop["examples"]  = v
                        sync_yaml()

                with rb[3]:
                    v = st.text_input("", value=prop.get("tags",""), key=f"ptag_{tid}_{pid}",
                                      placeholder="pii, fk:table, pk", label_visibility="collapsed")
                    if v != prop.get("tags"): prop["tags"] = v; sync_yaml()

                # Thin divider between columns
                st.markdown('<hr style="margin:0.15rem 0;border-color:var(--gray2)">', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("＋  Add Column", key=f"add_prop_{tid}", use_container_width=False):
                table["properties"].append(_new_prop()); sync_yaml(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Table", type="primary", key="btn_add_table"):
        tables.append(_new_table()); sync_yaml(); st.rerun()
