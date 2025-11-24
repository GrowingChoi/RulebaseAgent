import json
from typing import List, Dict

from app.config import client, MODEL_NAME


class Planner:
    """
    사용자의 질문 + 메모리 컨텍스트를 보고
    어떤 Tool을 어떤 입력으로 호출할지 계획을 세우는 모듈.
    """

    def __init__(self, tool_names: List[str]):
        self.tool_names = tool_names

    def plan(self, user_query: str, memory_context: str) -> Dict:
        """
        LLM에게 JSON 형태의 플랜을 생성하도록 요청.
        {
          "tool": "search" | "summarize" | "extract_clause" | "final_answer",
          "tool_input": { ... },
          "reason": "왜 이 액션을 선택했는지",
          "is_final": bool
        }
        """
        tools_str = ", ".join(self.tool_names)
        context_part = f"최근 대화 컨텍스트:\n{memory_context}\n\n" if memory_context else ""

        prompt = f"""
너는 'RulebaseAgent'라는 규정 분석 에이전트의 플래너야.
사용자의 질문에 답하기 위해 다음 중 하나의 도구를 선택해 행동 계획을 세워야 한다.

사용 가능한 도구들:
- search: 규정 데이터에서 관련 내용을 찾아온다.
- summarize: 규정 내용 여러 개를 받아 핵심만 요약한다.
- extract_clause: 규정 내용 여러 개를 받아 조항 단위로 정리한다.
- final_answer: 더 이상 도구 호출이 필요 없을 때 최종 답변을 만든다.

반드시 JSON만 반환해야 한다. 설명 텍스트는 포함하지 마라.

JSON 필드:
- tool: "{tools_str}" 중 하나
- tool_input: 도구에 넘길 입력 (딕셔너리)
- reason: 왜 이 도구를 선택했는지 한국어로 간략히
- is_final: true/false

{context_part}
[사용자 질문]
{user_query}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "너는 Tool-Using Agent의 플래너로서, 항상 유효한 JSON만 생성해야 한다."
                },
                {"role": "user", "content": prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()

        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            # 실패 시 기본 플랜 (search 한 번)
            plan = {
                "tool": "search",
                "tool_input": {"query": user_query},
                "reason": "JSON 파싱 실패로 기본 search를 수행",
                "is_final": False,
            }
        return plan
