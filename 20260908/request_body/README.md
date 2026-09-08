pip install requests 

POST요청을 보내려면 requests 라이브러리 가 필요하다. 
다음과 같이 요청이 가능하다.


import requests 

response = requests.post(
    "http://127.0.0.1:8000/items/",
    json={
        "name": "노트북",
        "price": 1500000,
    },
)

print(response.status_code)  # 200
print(response.json())


서버를 열어 놓은 상태에서 python requests_post.py

요청한 방법	응답을 받는 곳
브라우저 주소창에 URL 입력 → GET	브라우저가 응답을 화면에 표시
requests.post() 실행 → POST	파이썬이 응답을 response에 저장


즉, GET과 POST의 차이 때문에 화면이 바뀌는 건 아니고, 누가 요청했는지가 달라서 그래요.
GET도 파이썬에서 호출하면 브라우저는 바뀌지 않아요.
response = requests.get("http://127.0.0.1:8000/items/")
print(response.text)  # 터미널에 출력
위 코드는 해당 주소에 @app.get("/items/")이 등록되어 있을 때 사용할 수 있어요.
반대로 /docs에서 POST를 보내면 그 화면의 Response body에 응답이 표시돼요.

즉, 웹사이트에서는 변경은 없고 Post에서 요청한 정보를 받는 느낌
Post로 데이터가 변경되면서 화면이 바뀔 수는 있지만 현재 해당 부분은 구현이 안되서 값만 전달 받음
--------------------------------------------------
**두개가 붙은 거는 언패킹 키와 밸류를 분리하여 저장
item.model_dump()와 **item.model_dump
result = {"item": data}
#{"item": {"name": "노트북", "price": 1500000.0}}
result = {"id": 1, **data}
#{"id": 1, "name": "노트북", "price": 1500000.0}