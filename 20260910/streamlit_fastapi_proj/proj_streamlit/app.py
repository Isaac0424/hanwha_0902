import streamlit as st 
import numpy as np
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st. title("Streamlit & FastAPI Example")

#입력 폼 구성
with st.form("user_form"):
    name = st.text_input("이름", value = "홍길동")
    age = st.number_input("나이", min_value=1,max_value=120,value=20)
    submit_button = st.form_submit_button("백엔드로 전송")

if submit_button:
    #FastAPI로 보낼 데이터 페이로드
    payload = {
        "name": name,
        "age": age
    }
    
    try:
        #FastAPI / predict 앤드포인트에 POST 요철
        response = requests.post(f"{FASTAPI_URL}/predict", json=payload)
        if response.status_code == 200:
            result = response.json()
            st.success("FastAPI 응답성공!")
            st.write(f"저장된 요청 ID: {result['request_id']}")
            st.write(f"**결과:** {result['result_message']}")
        else:
            st.error(f"오류 발생 (상태 코드: {response.status_code})")
    except requests.exceptions.ConnectionError:
        st.error(f"FastAPI 서버에 연결할 수 없습니다. 백엔드 서버가 실행중인지 확인해주세요.")