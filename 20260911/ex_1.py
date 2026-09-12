import os
from openai import OpenAI

# .env를 읽기 위함
# from pathlib import Path
# from dotenv import load_dotenv
# load_dotenv(Path(__file__).with_name(".env"))
# load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")

client = OpenAI(api_key=api_key)
response = client.responses.create(
    model="gpt-5-mini",
    input="Write a one-sentence what Jesus said.",
)

print(response.output_text)

from google import genai

# 클라이언트 생성 (GOOGLE_API_KEY 환경변수 자동 감지)
client_genai = genai.Client()

# 모델 호출
response_genai = client_genai.models.generate_content(
    model='gemini-3.6-flash',
    contents='파이썬의 주요 장점 3가지를 알려줘.'
)

print(response_genai.text)