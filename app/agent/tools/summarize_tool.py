# app/agent/tools/summarize_tool.py
from typing import List, Dict, Any

from app.config import client, MODEL_NAME
from .base import Tool


class SummarizeTool(Tool):
    """
    규정 검색 결과들을 짧게 요약하는 Tool.
    """

    name = "summarize"
    description = "검색된 규정 텍스트들을 사용자 질문에 맞게 한국어로 요약하는 Tool"

    def run(self, *, user_query: str, tool_input: Dict[str, Any]) -> str:
        texts: List[str] = tool_input.get("texts") or []

        if not texts:
            return "summarize 할 텍스트가 없습니다."

        joined = "\n\n".join(texts)

        prompt = f"""
                    당신은 회사 내부 규정과 정책을 쉽게 설명해주는 한국어 규정 전문가입니다.

                    아래는 사용자의 질문과, 그와 관련된 규정 일부입니다.
                    사용자의 질문에 답을 줄 수 있도록 핵심 내용만 간결하게 요약해 주세요.

                    [사용자 질문]
                    {user_query}

                    [관련 규정 내용]
                    {joined}

                    요구사항:
                    - 중요한 조건, 예외 사항, 숫자/기준은 최대한 유지하세요.
                    - 불필요한 서론/결론은 빼고, 핵심 정책만 정리하세요.
                    - 한국어로 5~7문장 정도로 정리해 주세요.
                """.strip()

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "너는 규정과 정책을 잘 설명해주는 한국어 규정 전문가야."
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
