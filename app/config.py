import os
from typing import Final

from dotenv import load_dotenv
from openai import OpenAI

"""
OpenAI 클라이언트 및 기본 모델 설정 모듈.
환경 변수에서 API 키와 모델 이름을 읽어온다.
"""

load_dotenv()

MODEL_NAME: Final[str] = os.getenv("OPENAI_MODEL", "gpt-5-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

__all__ = ["client", "MODEL_NAME"]
