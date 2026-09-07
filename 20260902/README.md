# Python 실행 시간 측정 데코레이터 예제

Python 데코레이터를 사용하여 함수의 실행 시간을 측정하고, 과목별 교육 시간을 출력하는 예제입니다.

## 주요 기능

- `runtimeWrapper` 데코레이터를 통한 실행 시간 측정
- `DEBUG` 설정에 따른 디버그/릴리스 모드 분기
- 과목별 교육 시간 출력
- 함수 메타데이터 보존을 위한 `functools.wraps` 사용

## 실행 방법

Windows 터미널에서 다음 명령을 실행합니다.

```powershell
python 20260902\wrapper_decorator_test.py
```

## 출력 예시

```text
-------------------------------
AI 서비스 백엔드 프로그래밍 실무
================================
파이썬 기본 문법, 시간: 8
클래스, 시간: 8
데코레이터, 시간: 8
예외 처리, 시간: 8
로깅, 시간: 8
-------------------------------
Function name: printSchedule
Execution time: 0.0001234567 seconds
-------------------------------
```

## 설정

`DEBUG` 값을 변경하여 실행 시간 측정 여부를 설정할 수 있습니다.

```python
DEBUG = True
```

- `True`: 함수 실행 시간과 디버그 정보 출력
- `False`: 함수 결과만 출력

## 파일 구조

```text
hanwha_0902/
├── README.md
└── 20260902/
    └── wrapper_decorator_test.py
```