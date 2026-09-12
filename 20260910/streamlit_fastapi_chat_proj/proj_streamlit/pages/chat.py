import requests
import streamlit as st

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("채팅")

if (
    "name" not in st.session_state
    or not st.session_state.name
    or "session_token" not in st.session_state
):
    st.switch_page("pages/home.py")

session_data = {
    "name": st.session_state.name,
    "session_token": st.session_state.session_token,
}

if st.sidebar.button("로그아웃"):
    requests.post(f"{FASTAPI_URL}/logout", json=session_data)
    st.session_state.clear()
    st.switch_page("pages/home.py")

st.write(f"{st.session_state.name}님, 환영합니다.")


@st.fragment(run_every="2s")
def render_chat_messages():
    heartbeat_response = requests.post(
        f"{FASTAPI_URL}/heartbeat",
        json=session_data,
    )
    if not heartbeat_response.ok:
        st.session_state.clear()
        st.switch_page("pages/home.py")

    messages_response = requests.get(f"{FASTAPI_URL}/messages")
    if messages_response.ok:
        st.session_state.messages = messages_response.json()
    elif "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.write(f"{message['name']}: {message['message']}")


render_chat_messages()

prompt = st.chat_input("메시지를 입력하세요.")
if prompt:
    response = requests.post(
        f"{FASTAPI_URL}/send_messages",
        json={**session_data, "message": prompt},
    )
    if response.ok:
        st.rerun()
    else:
        st.error("메시지를 저장하지 못했습니다.")