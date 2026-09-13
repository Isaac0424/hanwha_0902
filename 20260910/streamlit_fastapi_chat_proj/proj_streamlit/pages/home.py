import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("채팅 참여")

if "name" not in st.session_state:
    st.session_state.name = ""

with st.form("input_user_name"):
    name = st.text_input("이름")
    register_button = st.form_submit_button("새 이름 등록")
    login_button = st.form_submit_button("기존 이름 로그인")

if register_button or login_button:
    if name.strip():
        endpoint = "/init_name" if register_button else "/login_name"
        response = requests.post(
            f"{FASTAPI_URL}{endpoint}",
            json={"name": name.strip()},
        )
        if response.ok:
            st.session_state.name = response.json()["name"]
            st.session_state.session_token = response.json()["session_token"]
            st.switch_page("pages/chat.py")
        elif register_button and response.status_code == 409:
            st.error("이미 사용 중인 이름입니다. 기존 이름으로 로그인해 주세요.")
        elif login_button and response.status_code == 404:
            st.error("등록된 이름이 없습니다. 새 이름을 등록해 주세요.")
        elif login_button and response.status_code == 409:
            st.error("이미 다른 세션에서 사용 중인 이름입니다.")
        else:
            st.error("이름을 처리하지 못했습니다.")
    else:
        st.error("이름을 입력해 주세요.")