import streamlit as st

# 로그인 역할을 세션에 저장합니다.
if "role" not in st.session_state:
    st.session_state.role = None

# 선택 가능한 사용자 역할입니다.
ROLES = [None, "Requester", "Responder", "Admin"]


# 역할을 선택하는 로그인 화면입니다.
def login():
    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)
    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()


# 세션을 초기화하고 로그인 화면으로 돌아갑니다.
def logout():
    st.session_state.role = None
    st.rerun()

# 현재 로그인한 역할입니다.
role = st.session_state.role

# 계정 관련 페이지입니다.
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

# 요청자용 페이지입니다.
request_1 = st.Page(
    "request/request_1.py",
    title="Request 1",
    icon=":material/help:",
    default=(role == "Requester"),
)
request_2 = st.Page(
    "request/request_2.py", title="Request 2", icon=":material/bug_report:"
)

# 응답자용 페이지입니다.
respond_1 = st.Page(
    "respond/respond_1.py",
    title="Respond 1",
    icon=":material/healing:",
    default=(role == "Responder"),
)
respond_2 = st.Page(
    "respond/respond_2.py", title="Respond 2", icon=":material/handyman:"
)

# 관리자용 페이지입니다.
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")

# 네비게이션에 사용할 페이지 그룹입니다.
account_pages = [logout_page, settings]
request_pages = [request_1, request_2]
respond_pages = [respond_1, respond_2]
admin_pages = [admin_1, admin_2]

# 앱 제목과 로고를 설정합니다.
st.title("Request manager")
st.logo("images/horizontal_your_logo_here.png", icon_image="images/icon_cat.png")

# 역할에 따라 노출할 페이지를 구성합니다.
page_dict = {}

if st.session_state.role in ["Requester", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role in ["Responder", "Admin"]:
    page_dict["Respond"] = respond_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

# 로그인 여부에 따라 네비게이션을 표시합니다.
if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

# 현재 페이지를 실행합니다.
pg.run()