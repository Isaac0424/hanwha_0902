import streamlit as st 

home_page = st.Page("pages/home.py", title="이름 입력", default=True)
chat_page = st.Page("pages/chat.py", title="채팅")

navigation = st.navigation([home_page, chat_page], position="hidden")
navigation.run()

