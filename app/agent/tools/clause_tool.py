# app/agent/tools/clause_tool.py
from typing import List, Dict, Any

from app.config import client, MODEL_NAME
from .base import Tool


class ClauseTool(Tool):
    """
    규정에서 '어떤 조항이 어떤 내용을 말하는지'를 좀 더 구조화해서 뽑아주는 Tool.
    """

    name = "extract_clause"
    description = "규정 텍스트에서 핵심 조항과 요지를 구조적으로 정리하는 Tool"

    def run(self, *, user_query: str, tool_input: Dict[str, Any]) -> str:
        texts: List[str] = tool_input.get("texts") or []

        if not texts:
            return "추출할 규정 텍스트가 없습니다."

        joined = "\n\n".join(texts)

        prompt = f"""
                    당신은 회사 규정/내부 지침에서 핵심 조항만 뽑아 정리해주는 조항 정리 전문가입니다.

                    [사용자 질문]
                    {user_query}

                    [관련 규정 원문]
                    {joined}

                    아래 형식에 맞춰서 정리해 주세요.

                    1. 관련 조항 요약
                    - 조항 번호(있다면): ...
                    - 이 조항이 말하고 있는 핵심 내용: ...

                    2. 사용자 질문과의 관계
                    - 이 조항이 사용자 질문과 어떤 관련이 있는지: ...

                    3. 실제 적용 시 주의할 점
                    - 예외나 추가로 확인해야 할 부분이 있다면 간단히 정리

                    한국어로 간결하게 정리해 주세요.
                """.strip()

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
