# app/agent/tools/summarize_tool.py
from typing import List

from app.config import client, MODEL_NAME


class SummarizeTool:
    """
    규정 검색 결과들을 짧게 요약하는 Tool.
    """

    name = "summarize"

    def run(self, texts: List[str], user_query: str) -> str:
        joined = "\n\n".join(texts)
        prompt = f"""
아래는 규정 문서의 일부 내용입니다. 사용자의 질문에 답변할 수 있도록
관련된 부분을 중심으로 간단하고 명확하게 요약해 주세요.

[사용자 질문]
{user_query}

[관련 규정 내용]
{joined}
"""
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
