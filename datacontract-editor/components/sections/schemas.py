"""Schemas section — tables and fields builder."""
import streamlit as st
import uuid
from utils.templates import FIELD_TYPES
from utils.state import sync_yaml


def _new_field():
    return {
        "id": str(uuid.uuid4())[:8], "name": "", "type": "string",
        "required": False, "unique": False, "pii": False, "nullable": True,
        "description": "", "example": "", "enum_values": "", "tags": "",
    }


def _new_table():
    return {"id": str(uuid.uuid4())[:8], "name": "", "description": "", "tags": "", "fields": [_new_field()]}


def render():
    st.markdown('<div class="section-header">🗄️ Schemas & Tables</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Define los modelos de datos: tablas, campos, tipos y restricciones.</div>', unsafe_allow_html=True)

    tables = st.session_state["tables"]
    if not tables:
        st.info("No tables defined yet. Click **＋ Add Table** to start building your schema.")

    for t_idx, table in enumerate(tables):
        tid = table.get("id", str(t_idx))
        with st.expander(f"📊  {table['name'] or '(unnamed table)'}", expanded=True):
            tc1, tc2, tc3, tc_del = st.columns([3, 4, 3, 1])
            with tc1:
                v = st.text_input("Table name *", value=table["name"], key=f"tname_{tid}", placeholder="e.g. orders")
                if v != table["name"]: table["name"] = v; sync_yaml()
            with tc2:
                v = st.text_input("Description", value=table["description"], key=f"tdesc_{tid}",
                                  placeholder="What does this table contain?")
                if v != table["description"]: table["description"] = v; sync_yaml()
            with tc3:
                v = st.text_input("Tags", value=table.get("tags",""), key=f"ttags_{tid}",
                                  placeholder="orders, raw")
                if v != table.get("tags"): table["tags"] = v; sync_yaml()
            with tc_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"del_table_{tid}"):
                    tables.pop(t_idx); sync_yaml(); st.rerun()

            st.markdown('<div class="fields-header">Fields</div>', unsafe_allow_html=True)
            _render_fields(table, tid)

            if st.button("＋ Add Field", key=f"add_field_{tid}"):
                table["fields"].append(_new_field()); sync_yaml(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Table", type="primary", key="btn_add_table"):
        tables.append(_new_table()); sync_yaml(); st.rerun()


def _render_fields(table, tid):
    fields = table["fields"]
    cols_hdr = st.columns([3, 2, 1, 1, 1, 1, 3, 2, 1])
    for col, lbl in zip(cols_hdr, ["Field Name *","Type","Req","Uniq","PII","Null","Description","Example / Enum",""]):
        col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for f_idx, field in enumerate(fields):
        fid = field.get("id", str(f_idx))
        fc = st.columns([3, 2, 1, 1, 1, 1, 3, 2, 1])

        with fc[0]:
            v = st.text_input("", value=field["name"], key=f"fn_{tid}_{fid}",
                              placeholder="field_name", label_visibility="collapsed")
            if v != field["name"]: field["name"] = v; sync_yaml()

        with fc[1]:
            idx = FIELD_TYPES.index(field["type"]) if field["type"] in FIELD_TYPES else 0
            v = st.selectbox("", FIELD_TYPES, index=idx, key=f"ft_{tid}_{fid}", label_visibility="collapsed")
            if v != field["type"]: field["type"] = v; sync_yaml()

        for fc_idx, fkey in [(2,"required"),(3,"unique"),(4,"pii"),(5,"nullable")]:
            with fc[fc_idx]:
                v = st.checkbox("", value=field.get(fkey, fkey=="nullable"), key=f"f{fkey}_{tid}_{fid}", label_visibility="collapsed")
                if v != field.get(fkey): field[fkey] = v; sync_yaml()

        with fc[6]:
            v = st.text_input("", value=field["description"], key=f"fdesc_{tid}_{fid}",
                              placeholder="Description", label_visibility="collapsed")
            if v != field["description"]: field["description"] = v; sync_yaml()

        with fc[7]:
            hint = "enum: val1, val2" if field["type"] == "string" else "example"
            cur = field.get("enum_values") or field.get("example","")
            v = st.text_input("", value=cur, key=f"fex_{tid}_{fid}", placeholder=hint, label_visibility="collapsed")
            key = "enum_values" if field["type"] == "string" else "example"
            if v != field.get(key,""): field[key] = v; sync_yaml()

        with fc[8]:
            if st.button("✕", key=f"del_f_{tid}_{fid}"):
                fields.pop(f_idx); sync_yaml(); st.rerun()
