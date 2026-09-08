import requests 

response = requests.post(
    "http://127.0.0.1:8000/items/",
    json={
        "name": "노트북",
        "price": 1500000,
        "tax": 50000
    },
)

print(response.status_code)  # 200
print(response.json())
