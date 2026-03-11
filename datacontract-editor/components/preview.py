"""
Preview & Validate tab — rendered HTML view of the data contract.
"""
import streamlit as st
import yaml
from utils.validator import validate_yaml


QUALITY_BADGE = {
    "draft":      ("🟡", "#f59e0b"),
    "active":     ("🟢", "#10b981"),
    "deprecated": ("🟠", "#f97316"),
    "retired":    ("🔴", "#ef4444"),
}

# Labels para el preview del panel derecho (sección activa)
SECTION_LABELS = {
    "fundamentals": "Fundamentals",
    "terms": "Terms of Use",
    "schemas": "Schemas & Tables",
    "servers": "Servers",
    "team": "Team",
    "support": "Support",
    "roles": "Roles",
    "pricing": "Pricing",
    "sla": "SLA",
}


def render_right_panel_preview(yaml_str: str, active_section: str):
    """Preview compacto para el panel derecho: card del contrato + resumen de la sección activa."""
    try:
        doc = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        st.markdown('<div class="right-preview-card right-preview-error">⚠ Invalid YAML</div>', unsafe_allow_html=True)
        return
    info = doc.get("info", {})
    cid = doc.get("id", "")
    title = info.get("title", "Untitled Contract")
    version = info.get("version", "—")
    status = info.get("status", "draft")
    owner = info.get("owner", "—")
    tags = info.get("tags", [])
    badge_icon, badge_color = QUALITY_BADGE.get(status, ("⚪", "#6b7280"))
    tag_pills = " ".join(f'<span class="preview-tag">{t}</span>' for t in tags) if tags else '<span class="preview-tag">—</span>'
    section_title = SECTION_LABELS.get(active_section, active_section)

    # Card principal (estilo referencia: título, id versión, tags, status)
    st.markdown(f"""
<div class="right-preview-card">
  <div class="right-preview-header">
    <span class="right-preview-icon">📋</span>
    <span class="right-preview-title">{title}</span>
  </div>
  <div class="right-preview-meta">{cid or "—"} · v{version}</div>
  <div class="right-preview-tags">
    {tag_pills}
    <span class="preview-badge" style="background:{badge_color}22;color:{badge_color};border:1px solid {badge_color}44;">{badge_icon} {str(status).upper()}</span>
    <span class="right-preview-odcs">ODCS 1.1.0</span>
  </div>
  <div class="right-preview-section-title">{section_title}</div>
  <div class="right-preview-section-desc">Resumen de la sección actual según el YAML.</div>
  <dl class="right-preview-dl">
    <dt>Name</dt><dd>{info.get("title", "—")}</dd>
    <dt>ID</dt><dd>{cid or "—"}</dd>
    <dt>Version</dt><dd>{version}</dd>
    <dt>Status</dt><dd>{str(status)}</dd>
    <dt>Owner</dt><dd>{owner or "—"}</dd>
  </dl>
</div>
""", unsafe_allow_html=True)

    # Si la sección tiene datos específicos en el doc, mostrar un resumen extra
    if active_section == "schemas" and doc.get("models"):
        models = doc.get("models", {})
        tables = ", ".join(models.keys()) if models else "—"
        st.markdown(f'<div class="right-preview-extra"><b>Tables:</b> {tables}</div>', unsafe_allow_html=True)
    elif active_section == "servers" and doc.get("servers"):
        servers = list(doc.get("servers", {}).keys())
        st.markdown(f'<div class="right-preview-extra"><b>Environments:</b> {", ".join(servers) or "—"}</div>', unsafe_allow_html=True)


def render_preview():
    yaml_str = st.session_state.get("yaml_content", "")

    col_prev, col_val = st.columns([3, 2])

    with col_val:
        st.markdown('<div class="section-header">Validation</div>', unsafe_allow_html=True)
        if st.button("▶  Run Validation", type="primary", key="btn_validate_preview"):
            result = validate_yaml(yaml_str)
            st.session_state["validation_result"] = result

        result = st.session_state.get("validation_result")
        if result is None:
            st.info("Click **Run Validation** to check your contract.")
        else:
            _render_validation_panel(result)

    with col_prev:
        st.markdown('<div class="section-header">Contract Preview</div>', unsafe_allow_html=True)
        try:
            doc = yaml.safe_load(yaml_str) or {}
            _render_contract_html(doc)
        except yaml.YAMLError as e:
            st.error(f"Cannot render preview — YAML error: {e}")


def _render_validation_panel(result):
    total = len(result.issues)
    errors = len(result.errors)
    warns = len(result.warnings)
    infos = len(result.infos)

    if result.is_valid:
        st.markdown(
            '<div class="val-banner val-ok">✅ Valid contract</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="val-banner val-fail">❌ {errors} error(s)</div>',
            unsafe_allow_html=True,
        )

    # Summary cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Errors", errors, delta=None)
    c2.metric("Warnings", warns, delta=None)
    c3.metric("Info", infos, delta=None)

    if result.issues:
        st.markdown("---")
        for issue in result.issues:
            icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            st.markdown(
                f"{icon} **{issue.path}** — {issue.message}",
                help=issue.severity,
            )


def _render_contract_html(doc: dict):
    info = doc.get("info", {})
    title = info.get("title", "Untitled Contract")
    version = info.get("version", "—")
    owner = info.get("owner", "—")
    status = info.get("status", "draft")
    description = info.get("description", "")
    tags = info.get("tags", [])
    cid = doc.get("id", "")

    badge_icon, badge_color = QUALITY_BADGE.get(status, ("⚪", "#6b7280"))
    tag_pills = " ".join(
        f'<span class="preview-tag">{t}</span>' for t in tags
    )

    # Header card
    st.markdown(f"""
<div class="preview-card preview-header-card">
  <div class="preview-title">{title}</div>
  <div class="preview-meta-row">
    <span class="preview-version">v{version}</span>
    <span class="preview-badge" style="background:{badge_color}22;color:{badge_color};border:1px solid {badge_color}44;">
      {badge_icon} {status.upper()}
    </span>
    <span class="preview-owner">👤 {owner}</span>
  </div>
  {f'<div class="preview-id">{cid}</div>' if cid else ''}
  {f'<div class="preview-desc">{description}</div>' if description else ''}
  {f'<div class="preview-tags">{tag_pills}</div>' if tag_pills else ''}
</div>
""", unsafe_allow_html=True)

    # Models
    models = doc.get("models", {})
    if models:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Models</div>',
                    unsafe_allow_html=True)
        for tname, tdef in models.items():
            if not isinstance(tdef, dict):
                continue
            tdesc = tdef.get("description", "")
            fields = tdef.get("fields", {}) or {}
            field_count = len(fields)

            rows = ""
            for fname, fdef in fields.items():
                if not isinstance(fdef, dict):
                    continue
                ftype = fdef.get("type", "—")
                req = "✓" if fdef.get("required") else ""
                uniq = "✓" if fdef.get("unique") else ""
                pii = "🔒" if fdef.get("pii") else ""
                fdesc = fdef.get("description", "")
                rows += f"""
<tr>
  <td class="tbl-fname">{fname}</td>
  <td class="tbl-ftype"><span class="type-badge">{ftype}</span></td>
  <td class="tbl-center">{req}</td>
  <td class="tbl-center">{uniq}</td>
  <td class="tbl-center">{pii}</td>
  <td class="tbl-fdesc">{fdesc}</td>
</tr>"""

            st.markdown(f"""
<div class="preview-card">
  <div class="model-title">📊 {tname}
    <span class="model-count">{field_count} field{'s' if field_count != 1 else ''}</span>
  </div>
  {f'<div class="model-desc">{tdesc}</div>' if tdesc else ''}
  <table class="field-table">
    <thead>
      <tr>
        <th>Field</th><th>Type</th>
        <th class="tbl-center">Required</th>
        <th class="tbl-center">Unique</th>
        <th class="tbl-center">PII</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    # Service Levels
    sla = doc.get("servicelevels", {})
    if sla:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Service Levels</div>',
                    unsafe_allow_html=True)
        sla_html = ""
        for k, v in sla.items():
            if isinstance(v, dict):
                desc = v.get("description", "")
                detail = v.get("percentage") or v.get("threshold") or v.get("responseTime") or ""
                sla_html += f'<div class="sla-item"><b>{k}</b>: {desc} <span class="sla-val">{detail}</span></div>'
        st.markdown(f'<div class="preview-card">{sla_html}</div>', unsafe_allow_html=True)

    # Terms
    terms = doc.get("terms", {})
    if terms:
        st.markdown('<div class="section-header" style="margin-top:1.5rem">Terms</div>',
                    unsafe_allow_html=True)
        terms_html = "".join(
            f'<div class="sla-item"><b>{k}</b>: {v}</div>'
            for k, v in terms.items()
        )
        st.markdown(f'<div class="preview-card">{terms_html}</div>', unsafe_allow_html=True)
