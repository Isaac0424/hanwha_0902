import streamlit as st 
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st. title("Streamlit & FastAPI Chat Example")

with st.form("add_user_name"):
    name = st.text_input("이름", value = "홍길동")
    submit_button = st.form_submit_button("백엔드로 전송")

if submit_button:
    payload = {
        "name": name
    }
    
    try:
        response = requests.post(f"{FASTAPI_URL}")
        pass
    except:
        pass
prompt = st.chat_input("Say something")
if prompt:
    response = requests.post(f"{FASTAPI_URL}/send_messages", json=prompt)
    st.write(f"User: {prompt}")
    
