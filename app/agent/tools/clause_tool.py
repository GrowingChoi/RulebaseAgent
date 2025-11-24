# app/agent/tools/clause_tool.py
from typing import List

from app.config import client, MODEL_NAME


class ClauseTool:
    """
    규정에서 '어떤 조항이 어떤 내용을 말하는지'를 좀 더 구조화해서 뽑아주는 Tool.
    """

    name = "extract_clause"

    def run(self, texts: List[str], user_query: str) -> str:
        joined = "\n\n".join(texts)
        prompt = f"""
아래 규정 내용에서, 사용자의 질문과 직접적으로 연관된 조항(조건, 허용 범위, 예외)을
조항 단위로 정리해 주세요.

[사용자 질문]
{user_query}

[관련 규정 내용]
{joined}

출력 형식 예시:
- 관련 조항 요약 1
- 관련 조항 요약 2
- ...

꼭 한국어로 간결하게 정리해 주세요.
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "너는 복잡한 규정에서 사용자에게 필요한 조항만 뽑아서 알려주는 조항 정리 전문가야."
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
