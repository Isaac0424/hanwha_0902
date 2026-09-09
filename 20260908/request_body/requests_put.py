import requests

# URL의 1은 item_id, params는 쿼리 파라미터, json은 요청 본문이에요.
try:
    response = requests.put(
        "http://127.0.0.1:8000/items/*",
        json={"name": "노트북", "price": 1800000},
        timeout=10,
    )
    print(response.status_code)
    print(response.json())

except requests.exceptions.Timeout:
    print("서버 응답을 기다리다가 제한 시간을 넘었어요.")
    
print(response.status_code)
print(response.json())
