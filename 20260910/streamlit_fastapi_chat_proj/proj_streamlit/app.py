import streamlit as st 
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st. title("Streamlit & FastAPI Chat Example")

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
