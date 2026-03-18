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


def _lbl(text, small=False):
    size = "0.6rem" if small else "0.65rem"
    return st.markdown(
        f'<div style="font-family:var(--poppins);font-size:{size};font-weight:700;'
        f'color:var(--gray4);text-transform:uppercase;letter-spacing:0.08em;'
        f'margin-bottom:2px;margin-top:6px">{text}</div>',
        unsafe_allow_html=True
    )


def render():
    st.markdown('<div class="section-header">🗄️ Schema</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Modelo físico: tablas, columnas, tipos y restricciones de la fuente.</div>', unsafe_allow_html=True)

    tables = st.session_state["tables"]
    svs        = st.session_state.get("servers", [])
    stype      = svs[0].get("type", "oracle") if svs else "oracle"
    phys_hints = PHYSICAL_TYPES_MAP.get(stype, PHYSICAL_TYPES_MAP["default"])
    ph_hint    = phys_hints[0] if phys_hints else "VARCHAR2(n)"

    if not tables:
        st.info("Sin tablas. Haz clic en **＋ Add Table**.")

    for t_idx, table in enumerate(tables):
        tid    = table.get("id", str(t_idx))
        n_cols = len(table.get("properties", []))
        label  = f"📊  **{table['name'] or '(sin nombre)'}** · {table.get('physicalName','')} · {n_cols} col{'s' if n_cols!=1 else ''}"

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
                v = st.text_input("Tags", value=table.get("tags",""), key=f"ttag_{tid}", placeholder="fact-table")
                if v != table.get("tags"): table["tags"] = v; sync_yaml()
            with tc_del:
                if st.button("🗑", key=f"tdel_{tid}"):
                    tables.pop(t_idx); sync_yaml(); st.rerun()

            # Description — altura reducida
            v = st.text_area("Description", value=table.get("description",""), height=32,
                             key=f"tdesc_{tid}", placeholder="Descripción de la tabla...")
            if v != table.get("description"): table["description"] = v; sync_yaml()

            if not table.get("properties"):
                st.caption("Sin columnas.")

            # ── Column section ────────────────────────────────────────────────
            st.markdown(
                '<div class="fields-header" style="margin-top:0.5rem;margin-bottom:0">Columns</div>',
                unsafe_allow_html=True
            )

            # ── Per-column rows ───────────────────────────────────────────────
            # Layout: [Name(3) | PhysType(3) | PK(1) | Req(1) | Uniq(1) | Class(2) | Del(1)]
            # Sub-row: [BizName(3) | Desc(3) | Examples(3) | Tags(3)]
            COL_W_A = [3, 3, 1, 1, 1, 2, 1]
            COL_W_B = [3, 3, 3, 3]

            for f_idx, prop in enumerate(table.get("properties", [])):
                pid = prop.get("id", str(f_idx))

                # ── Row A: labels ─────────────────────────────────────────────
                if f_idx == 0:
                    la = st.columns(COL_W_A)
                    for col, lbl in zip(la, ["Column Name", "Physical Type", "PK", "Req", "Uniq", "Classification", ""]):
                        with col: _lbl(lbl)
                    lb = st.columns(COL_W_B)
                    for col, lbl in zip(lb, ["Business Name", "Description", "Examples / Enum", "Tags"]):
                        with col: _lbl(lbl, small=True)
                    st.markdown('<hr style="margin:0 0 0.3rem;border-color:var(--border2)">', unsafe_allow_html=True)

                # ── Row A: inputs ─────────────────────────────────────────────
                ra = st.columns(COL_W_A)

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
                        st.markdown("<div style='padding-top:6px'>", unsafe_allow_html=True)
                        v = st.checkbox("", value=bool(prop.get(pkey, False)),
                                        key=f"p{pkey}_{tid}_{pid}", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                        if v != prop.get(pkey): prop[pkey] = v; sync_yaml()

                with ra[5]:
                    cls_opts = [""] + CLASSIFICATION
                    idx = cls_opts.index(prop.get("classification","")) if prop.get("classification") in cls_opts else 0
                    v = st.selectbox("", cls_opts, index=idx, key=f"pcls_{tid}_{pid}",
                                     label_visibility="collapsed")
                    if v != prop.get("classification"): prop["classification"] = v; sync_yaml()

                with ra[6]:
                    st.markdown("<div style='padding-top:6px'>", unsafe_allow_html=True)
                    if st.button("✕", key=f"pdel_{tid}_{pid}"):
                        table["properties"].pop(f_idx); sync_yaml(); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # ── Row B: extended fields ────────────────────────────────────
                rb = st.columns(COL_W_B)

                with rb[0]:
                    v = st.text_input("", value=prop.get("businessName",""), key=f"pbn_{tid}_{pid}",
                                      placeholder="Business name", label_visibility="collapsed")
                    if v != prop.get("businessName"): prop["businessName"] = v; sync_yaml()

                with rb[1]:
                    v = st.text_input("", value=prop.get("description",""), key=f"pdesc_{tid}_{pid}",
                                      placeholder="Description", label_visibility="collapsed")
                    if v != prop.get("description"): prop["description"] = v; sync_yaml()

                with rb[2]:
                    cur = prop.get("lto_enum","") or prop.get("examples","")
                    v = st.text_input("", value=cur, key=f"pex_{tid}_{pid}",
                                      placeholder="val1, val2, val3", label_visibility="collapsed")
                    if v != cur:
                        prop["lto_enum"] = v; prop["examples"] = v; sync_yaml()

                with rb[3]:
                    v = st.text_input("", value=prop.get("tags",""), key=f"ptag_{tid}_{pid}",
                                      placeholder="pii, fk:table, pk", label_visibility="collapsed")
                    if v != prop.get("tags"): prop["tags"] = v; sync_yaml()

                # Thin separator between columns
                st.markdown(
                    '<hr style="margin:0.2rem 0;border-color:var(--gray2);border-style:dashed">',
                    unsafe_allow_html=True
                )

            if st.button("＋  Add Column", key=f"add_prop_{tid}"):
                table["properties"].append(_new_prop()); sync_yaml(); st.rerun()

    if st.button("＋  Add Table", type="primary", key="btn_add_table"):
        tables.append(_new_table()); sync_yaml(); st.rerun()
