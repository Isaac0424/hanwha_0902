import re

import requests

BASE_URL = "http://127.0.0.1:8000"
PHONE_NUMBER_PATTERN = r"^(01[016789])-?(\d{3,4})-?(\d{4})$"
DEFAULT_USER = {
    "name": "isaac",
    "age": 31,
    "phone_number": None,
}
DEFAULT_DELETE_USER_ID = 3


def input_user_information(use_default: bool = False) -> dict:
    if use_default:
        return DEFAULT_USER.copy()

    while True:
        name = input(f"이름 [{DEFAULT_USER['name']}]: ").strip()
        name = name or DEFAULT_USER["name"]
        if len(name) >= 3:
            break
        print("이름은 3글자 이상 입력하세요.")

    while True:
        try:
            age_input = input(f"나이 [{DEFAULT_USER['age']}]: ").strip()
            age = int(age_input or DEFAULT_USER["age"])
            if age >= 0:
                break
            print("나이는 0 이상이어야 합니다.")
        except ValueError:
            print("나이는 숫자로 입력하세요.")

    while True:
        phone_number = input(
            "전화번호(Enter=없음, 예: 01012345678): "
        ).strip()
        if not phone_number or re.fullmatch(PHONE_NUMBER_PATTERN, phone_number):
            break
        print("전화번호 형식이 올바르지 않습니다.")

    return {
        "name": name,
        "age": age,
        "phone_number": phone_number or None,
    }


def put_user(use_default: bool = False) -> dict:
    response = requests.put(
        f"{BASE_URL}/update/",
        json=input_user_information(use_default),
    )
    return {"status_code": response.status_code, "body": response.json()}


def delete_user(use_default: bool = False) -> dict:
    if use_default:
        user_id = DEFAULT_DELETE_USER_ID
    else:
        user_id_input = input(
            f"삭제할 사용자 ID [{DEFAULT_DELETE_USER_ID}]: "
        ).strip()
        user_id = int(user_id_input or DEFAULT_DELETE_USER_ID)

    response = requests.delete(f"{BASE_URL}/user-db/{user_id}")
    return {"status_code": response.status_code, "body": response.json()}


def print_response(response: dict) -> None:
    print(response["status_code"])
    print(response["body"])


def main() -> None:
    action = input("작업을 선택하세요 (put/delete) [put]: ").strip().lower()
    action = action or "put"

    use_default_input = input(
        "기본값을 사용하시겠습니까? (Y/n): "
    ).strip().lower() != "n"

    if action == "put":
        response = put_user(use_default_input)
    elif action == "delete":
        response = delete_user(use_default_input)
    else:
        raise ValueError("put 또는 delete를 입력하세요.")

    show_response = input("응답을 출력할까요? (Y/n): ").strip().lower() != "n"
    if show_response:
        print_response(response)


if __name__ == "__main__":
    main()
