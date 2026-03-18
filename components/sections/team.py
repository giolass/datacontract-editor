import streamlit as st, uuid
from utils.templates import TEAM_ROLES
from utils.state import sync_yaml


def render():
    st.markdown('<div class="section-header">👥 Team</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Stakeholders del contrato — propietarios, stewards, consumidores y DPO.</div>', unsafe_allow_html=True)

    team = st.session_state["team"]
    if not team:
        st.info("Sin miembros. Haz clic en **＋ Add Member**.")

    hc = st.columns([2, 3, 3, 2, 2, 1])
    for col, lbl in zip(hc, ["Username","Name","Email","Role","Date In",""]):
        col.markdown(f'<div class="field-col-hdr">{lbl}</div>', unsafe_allow_html=True)

    for i, m in enumerate(team):
        mid = m.get("id", str(i))
        mc = st.columns([2, 3, 3, 2, 2, 1])
        with mc[0]:
            v = st.text_input("", value=m.get("username",""), key=f"tm_un_{mid}", placeholder="user.name", label_visibility="collapsed")
            if v != m.get("username"): m["username"] = v; sync_yaml()
        with mc[1]:
            v = st.text_input("", value=m.get("name",""), key=f"tm_name_{mid}", placeholder="Full Name", label_visibility="collapsed")
            if v != m.get("name"): m["name"] = v; sync_yaml()
        with mc[2]:
            v = st.text_input("", value=m.get("email",""), key=f"tm_email_{mid}", placeholder="name@bpt.com.co", label_visibility="collapsed")
            if v != m.get("email"): m["email"] = v; sync_yaml()
        with mc[3]:
            idx = TEAM_ROLES.index(m.get("role","owner")) if m.get("role") in TEAM_ROLES else 0
            v = st.selectbox("", TEAM_ROLES, index=idx, key=f"tm_role_{mid}", label_visibility="collapsed")
            if v != m.get("role"): m["role"] = v; sync_yaml()
        with mc[4]:
            v = st.text_input("", value=m.get("dateIn",""), key=f"tm_date_{mid}", placeholder="YYYY-MM-DD", label_visibility="collapsed")
            if v != m.get("dateIn"): m["dateIn"] = v; sync_yaml()
        with mc[5]:
            if st.button("✕", key=f"tm_del_{mid}"):
                team.pop(i); sync_yaml(); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋  Add Member", type="primary", key="btn_add_member"):
        team.append({"id": str(uuid.uuid4())[:8], "username": "", "name": "",
                     "email": "", "role": "owner", "dateIn": ""})
        sync_yaml(); st.rerun()
