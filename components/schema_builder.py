"""
Schema Builder tab — visual form-based editor for models and fields.
Syncs to YAML automatically on every change.
"""
import streamlit as st
from utils.templates import FIELD_TYPES, STATUS_OPTIONS
from utils.builder import build_yaml_from_state
import uuid


# ─── helpers ─────────────────────────────────────────────────────────────────

def _sync():
    st.session_state["yaml_content"] = build_yaml_from_state()


def _new_field():
    return {
        "id": str(uuid.uuid4())[:8],
        "name": "",
        "type": "string",
        "required": False,
        "unique": False,
        "pii": False,
        "description": "",
        "example": "",
        "enum_values": "",
    }


def _new_table():
    return {
        "id": str(uuid.uuid4())[:8],
        "name": "",
        "description": "",
        "fields": [_new_field()],
    }


# ─── render ──────────────────────────────────────────────────────────────────

def render_schema_builder():
    st.markdown('<div class="section-header">Contract Metadata</div>', unsafe_allow_html=True)
    _render_metadata()

    st.markdown('<div class="section-header" style="margin-top:2rem">Models / Tables</div>',
                unsafe_allow_html=True)
    _render_tables()


def _render_metadata():
    meta = st.session_state["contract_meta"]

    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        v = st.text_input("Contract Title *", value=meta.get("title", ""), key="meta_title")
        if v != meta.get("title"):
            meta["title"] = v; _sync()
    with c2:
        v = st.text_input("Version *", value=meta.get("version", "1.0.0"), key="meta_version")
        if v != meta.get("version"):
            meta["version"] = v; _sync()
    with c3:
        idx = STATUS_OPTIONS.index(meta.get("status", "draft")) if meta.get("status") in STATUS_OPTIONS else 0
        v = st.selectbox("Status", STATUS_OPTIONS, index=idx, key="meta_status")
        if v != meta.get("status"):
            meta["status"] = v; _sync()

    c4, c5 = st.columns([3, 3])
    with c4:
        v = st.text_input("Contract ID (URN) *",
                          value=meta.get("id", "urn:datacontract:com:example:new"), key="meta_id")
        if v != meta.get("id"):
            meta["id"] = v; _sync()
    with c5:
        v = st.text_input("Owner *", value=meta.get("owner", ""), key="meta_owner")
        if v != meta.get("owner"):
            meta["owner"] = v; _sync()

    v = st.text_area("Description", value=meta.get("description", ""),
                     height=80, key="meta_desc")
    if v != meta.get("description"):
        meta["description"] = v; _sync()

    tags_raw = st.text_input("Tags (comma separated)",
                             value=", ".join(meta.get("tags", [])), key="meta_tags")
    tags_new = [t.strip() for t in tags_raw.split(",") if t.strip()]
    if tags_new != meta.get("tags"):
        meta["tags"] = tags_new; _sync()


def _render_tables():
    tables = st.session_state["tables"]

    if not tables:
        st.info("No tables yet. Click **Add Table** to start building your schema.")

    for t_idx, table in enumerate(tables):
        tid = table.get("id", str(t_idx))
        with st.expander(f"📊  {table['name'] or '(unnamed table)'}", expanded=True):
            # Table header row
            tc1, tc2, tc3 = st.columns([3, 5, 1])
            with tc1:
                v = st.text_input("Table name *", value=table["name"],
                                  key=f"tname_{tid}", placeholder="e.g. orders")
                if v != table["name"]:
                    table["name"] = v; _sync()
            with tc2:
                v = st.text_input("Description", value=table["description"],
                                  key=f"tdesc_{tid}", placeholder="What does this table contain?")
                if v != table["description"]:
                    table["description"] = v; _sync()
            with tc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"del_table_{tid}", help="Delete table"):
                    tables.pop(t_idx); _sync(); st.rerun()

            st.markdown('<div class="fields-header">Fields</div>', unsafe_allow_html=True)
            _render_fields(table, tid)

            if st.button("＋ Add Field", key=f"add_field_{tid}"):
                table["fields"].append(_new_field())
                _sync(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Table", type="primary", key="btn_add_table"):
        tables.append(_new_table())
        _sync(); st.rerun()


def _render_fields(table, tid):
    fields = table["fields"]

    # Column header labels
    cols_hdr = st.columns([3, 2, 1, 1, 1, 3, 2, 1])
    labels = ["Field Name *", "Type", "Required", "Unique", "PII",
              "Description", "Example / Enum", ""]
    for col, lbl in zip(cols_hdr, labels):
        col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for f_idx, field in enumerate(fields):
        fid = field.get("id", str(f_idx))
        fc = st.columns([3, 2, 1, 1, 1, 3, 2, 1])

        with fc[0]:
            v = st.text_input("", value=field["name"], key=f"fn_{tid}_{fid}",
                              placeholder="field_name", label_visibility="collapsed")
            if v != field["name"]:
                field["name"] = v; _sync()

        with fc[1]:
            idx = FIELD_TYPES.index(field["type"]) if field["type"] in FIELD_TYPES else 0
            v = st.selectbox("", FIELD_TYPES, index=idx, key=f"ft_{tid}_{fid}",
                             label_visibility="collapsed")
            if v != field["type"]:
                field["type"] = v; _sync()

        with fc[2]:
            v = st.checkbox("", value=field["required"], key=f"freq_{tid}_{fid}",
                            label_visibility="collapsed")
            if v != field["required"]:
                field["required"] = v; _sync()

        with fc[3]:
            v = st.checkbox("", value=field["unique"], key=f"funiq_{tid}_{fid}",
                            label_visibility="collapsed")
            if v != field["unique"]:
                field["unique"] = v; _sync()

        with fc[4]:
            v = st.checkbox("", value=field["pii"], key=f"fpii_{tid}_{fid}",
                            label_visibility="collapsed")
            if v != field["pii"]:
                field["pii"] = v; _sync()

        with fc[5]:
            v = st.text_input("", value=field["description"], key=f"fdesc_{tid}_{fid}",
                              placeholder="Description", label_visibility="collapsed")
            if v != field["description"]:
                field["description"] = v; _sync()

        with fc[6]:
            hint = "enum: val1, val2" if field["type"] == "string" else "example value"
            v = st.text_input("", value=field.get("enum_values") or field.get("example", ""),
                              key=f"fex_{tid}_{fid}",
                              placeholder=hint, label_visibility="collapsed")
            key = "enum_values" if field["type"] == "string" else "example"
            if v != field.get(key, ""):
                field[key] = v; _sync()

        with fc[7]:
            if st.button("✕", key=f"del_field_{tid}_{fid}", help="Remove field"):
                fields.pop(f_idx); _sync(); st.rerun()
