"""Quality section — ODCS declarative rules + DQX executable checks."""
import streamlit as st, uuid
from utils.templates import DQ_DIMENSIONS, DQ_SEVERITY, DQ_DRIVERS, DQX_ROW_CHECKS, DQX_CRITICALITY
from utils.state import sync_yaml


def _uid(): return str(uuid.uuid4())[:8]


def render():
    st.markdown('<div class="section-header">✅ Data Quality</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Reglas de calidad declarativas (ODCS) y checks ejecutables en Spark vía Databricks Labs DQX.</div>', unsafe_allow_html=True)

    tab_odcs, tab_dqx = st.tabs(["📋  ODCS Rules (declarative)", "⚡  DQX Checks (executable)"])

    # ── ODCS declarative rules ─────────────────────────────────────────────────
    with tab_odcs:
        st.markdown('<div class="section-desc">Reglas de calidad según el estándar ODCS — dimensión, severidad y elemento del contrato.</div>', unsafe_allow_html=True)
        rules = st.session_state["quality_rules"]

        if not rules:
            st.info("Sin reglas definidas. Haz clic en **＋ Add Rule**.")

        for i, r in enumerate(rules):
            rid = r.get("id", str(i))
            with st.container():
                c1, c2, c3, c4, c5, c_del = st.columns([3, 2, 2, 2, 3, 1])
                with c1:
                    v = st.text_input("Rule name *", value=r.get("rule",""), key=f"qr_rule_{rid}", placeholder="order_id_not_null")
                    if v != r.get("rule"): r["rule"] = v; sync_yaml()
                with c2:
                    idx = DQ_DIMENSIONS.index(r.get("dimension","completeness")) if r.get("dimension") in DQ_DIMENSIONS else 0
                    v = st.selectbox("Dimension", DQ_DIMENSIONS, index=idx, key=f"qr_dim_{rid}")
                    if v != r.get("dimension"): r["dimension"] = v; sync_yaml()
                with c3:
                    idx = DQ_SEVERITY.index(r.get("severity","error")) if r.get("severity") in DQ_SEVERITY else 0
                    v = st.selectbox("Severity", DQ_SEVERITY, index=idx, key=f"qr_sev_{rid}")
                    if v != r.get("severity"): r["severity"] = v; sync_yaml()
                with c4:
                    idx = DQ_DRIVERS.index(r.get("driver","operational")) if r.get("driver") in DQ_DRIVERS else 0
                    v = st.selectbox("Driver", DQ_DRIVERS, index=idx, key=f"qr_drv_{rid}")
                    if v != r.get("driver"): r["driver"] = v; sync_yaml()
                with c5:
                    v = st.text_input("Element", value=r.get("element",""), key=f"qr_elem_{rid}", placeholder="table.column")
                    if v != r.get("element"): r["element"] = v; sync_yaml()
                with c_del:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✕", key=f"qr_del_{rid}"):
                        rules.pop(i); sync_yaml(); st.rerun()

                v = st.text_input("Description", value=r.get("description",""), key=f"qr_desc_{rid}",
                                   placeholder="Describe the rule and its business impact")
                if v != r.get("description"): r["description"] = v; sync_yaml()
                st.markdown('<hr style="margin:0.4rem 0;border-color:#dde0f0">', unsafe_allow_html=True)

        if st.button("＋  Add ODCS Rule", type="primary", key="btn_add_qrule"):
            rules.append({"id": _uid(), "rule": "", "description": "", "dimension": "completeness",
                          "severity": "error", "driver": "operational", "element": "", "schedule": ""})
            sync_yaml(); st.rerun()

    # ── DQX executable checks ──────────────────────────────────────────────────
    with tab_dqx:
        st.markdown('<div class="section-desc">Checks ejecutables en Spark via <b>databricks-labs-dqx</b>. Se organizan por tabla y se almacenan como YAML en Databricks Volume.</div>', unsafe_allow_html=True)

        dqx = st.session_state["dqx_checks"]
        tables = st.session_state.get("tables", [])
        table_names = [t["name"] for t in tables if t.get("name","").strip()]

        if not table_names:
            st.warning("⚠️ Define tablas en la sección **Schema** para agregar DQX checks.")
            return

        # Table selector
        selected_table = st.selectbox("Table", table_names, key="dqx_table_sel")
        if selected_table not in dqx:
            dqx[selected_table] = []

        checks = dqx.get(selected_table, [])

        if not checks:
            st.info(f"Sin checks para **{selected_table}**. Haz clic en **＋ Add Check**.")

        # Column header
        ch1, ch2, ch3, ch4, ch5 = st.columns([2, 2, 3, 3, 1])
        for col, label in zip([ch1,ch2,ch3,ch4,ch5], ["Criticality","Function","Column / Target","Name (auto)","Del"]):
            col.markdown(f'<div class="field-col-hdr">{label}</div>', unsafe_allow_html=True)

        for i, c in enumerate(checks):
            cid = c.get("id", str(i))
            cc1, cc2, cc3, cc4, cc5 = st.columns([2, 2, 3, 3, 1])
            with cc1:
                idx = DQX_CRITICALITY.index(c.get("criticality","error")) if c.get("criticality") in DQX_CRITICALITY else 0
                v = st.selectbox("", DQX_CRITICALITY, index=idx, key=f"dqx_crit_{cid}", label_visibility="collapsed")
                if v != c.get("criticality"): c["criticality"] = v; sync_yaml()
            with cc2:
                idx = DQX_ROW_CHECKS.index(c.get("function","is_not_null")) if c.get("function") in DQX_ROW_CHECKS else 0
                v = st.selectbox("", DQX_ROW_CHECKS, index=idx, key=f"dqx_fn_{cid}", label_visibility="collapsed")
                if v != c.get("function"): c["function"] = v; sync_yaml()
            with cc3:
                # Populate column names from table schema
                tbl = next((t for t in tables if t["name"] == selected_table), None)
                col_opts = [""] + [p["name"] for p in (tbl.get("properties",[]) if tbl else []) if p.get("name")]
                cur_col = c.get("column","")
                if cur_col not in col_opts: col_opts.append(cur_col)
                idx = col_opts.index(cur_col) if cur_col in col_opts else 0
                v = st.selectbox("", col_opts, index=idx, key=f"dqx_col_{cid}", label_visibility="collapsed")
                if v != c.get("column"): c["column"] = v; sync_yaml()
            with cc4:
                # Auto-suggest name
                auto_name = f"{c.get('column','col')}_{c.get('function','check')}".replace(" ","_")
                cur_name = c.get("name","") or auto_name
                v = st.text_input("", value=cur_name, key=f"dqx_name_{cid}", label_visibility="collapsed")
                if v != c.get("name"): c["name"] = v; sync_yaml()
            with cc5:
                if st.button("✕", key=f"dqx_del_{cid}"):
                    checks.pop(i); sync_yaml(); st.rerun()

            # Extra args expander for complex checks
            fn = c.get("function","")
            if fn in ["is_in_list","is_not_in_list","is_not_null_and_is_in_list","is_in_range",
                      "is_not_in_range","is_not_less_than","is_not_greater_than","regex_match",
                      "is_data_fresh","foreign_key","sql_expression","is_aggr_not_less_than","is_aggr_not_greater_than"]:
                with st.expander(f"⚙ Extra arguments — {fn}", expanded=False):
                    v = st.text_area("Arguments (JSON)", value=c.get("extra_args",""), height=70,
                                     key=f"dqx_args_{cid}",
                                     placeholder=_arg_hint(fn))
                    if v != c.get("extra_args"): c["extra_args"] = v; sync_yaml()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("＋  Add DQX Check", type="primary", key=f"btn_add_dqx_{selected_table}"):
            checks.append({"id": _uid(), "criticality": "error", "name": "", "function": "is_not_null", "column": "", "extra_args": ""})
            dqx[selected_table] = checks; sync_yaml(); st.rerun()

        # DQX summary
        total = sum(len(v) for v in dqx.values())
        if total:
            st.markdown(f"""
            <div class="sla-summary" style="margin-top:1.5rem">
              <div style="font-family:var(--poppins);font-size:0.65rem;font-weight:700;color:var(--purple);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">DQX Checks Summary</div>
              {"".join(f'<div class="sla-row"><span>📊 {tname}</span><b>{len(chks)} checks</b></div>' for tname, chks in dqx.items() if chks)}
              <div class="sla-row"><span>Total</span><b>{total} checks</b></div>
            </div>
            """, unsafe_allow_html=True)


def _arg_hint(fn):
    hints = {
        "is_in_list": '{"allowed": ["val1", "val2", "val3"]}',
        "is_not_in_list": '{"forbidden": ["val1", "val2"]}',
        "is_not_null_and_is_in_list": '{"allowed": ["shipped","pending","cancelled"]}',
        "is_in_range": '{"min_limit": 0, "max_limit": 1000000}',
        "is_not_in_range": '{"min_limit": 0, "max_limit": 10}',
        "is_not_less_than": '{"limit": 0}',
        "is_not_greater_than": '{"limit": 9999}',
        "regex_match": '{"regex": "^[A-Z]{3}-\\\\d{8}$", "negate": false}',
        "is_data_fresh": '{"max_age_minutes": 1440}',
        "foreign_key": '{"columns": ["order_id"], "ref_columns": ["order_id"], "ref_table": "catalog.schema.table"}',
        "sql_expression": '{"expression": "col >= 0 AND col IS NOT NULL", "msg": "Invalid value"}',
        "is_aggr_not_less_than": '{"aggr_type": "count", "limit": 1}',
        "is_aggr_not_greater_than": '{"aggr_type": "count", "limit": 10000000}',
    }
    return hints.get(fn, '{"key": "value"}')
