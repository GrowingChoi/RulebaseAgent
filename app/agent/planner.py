# app/agent/planner.py
import json
from typing import List, Dict, Any

from app.config import client, MODEL_NAME


class Planner:
    """
    사용자의 질문 + 메모리 컨텍스트를 보고
    어떤 Tool을 어떤 입력으로 호출할지 계획을 세우는 모듈.
    """

    def __init__(self, tool_names: List[str]):
        """
        :param tool_names: 사용할 수 있는 tool 이름 리스트
                           예: ["search", "summarize", "extract_clause", "final_answer"]
        """
        self.tool_names = tool_names

    def plan(self, user_query: str, memory_context: str) -> Dict[str, Any]:
        """
        LLM에게 JSON 형태의 플랜을 생성하도록 요청.

        기대하는 JSON 구조:
        {
          "tool": "search" | "summarize" | "extract_clause" | "final_answer",
          "tool_input": { ... },
          "reason": "왜 이 액션을 선택했는지",
          "is_final": bool
        }
        """
        tools_str = ", ".join(self.tool_names)

        prompt = f"""
                    당신은 Tool-Using Agent의 플래너입니다.
                    아래 정보를 보고, 다음에 실행할 '단 한 번의' 액션을 JSON으로만 반환하세요.

                    [사용 가능한 Tool 목록]
                    {tools_str}

                    각 Tool의 의미 예시:
                    - search: 규정 데이터에서 관련 조항을 검색할 때 사용
                    - summarize: 이미 검색된 텍스트들을 요약해서 최종 답변을 만들 때 사용
                    - extract_clause: 규정에서 핵심 조항/조건만 구조적으로 정리할 때 사용
                    - final_answer: 더 이상 Tool을 호출할 필요 없이, 지금까지의 정보를 바탕으로 최종 답변을 생성할 때 사용

                    중요 규칙:
                    1. "tool" 값이 "final_answer"인 경우,
                    반드시 "tool_input" 안에 "answer"라는 문자열 필드를 포함해야 합니다.
                    - 이 "answer" 필드에는 사용자에게 바로 보여줄 최종 한국어 답변 전체를 넣어야 합니다.
                    - 즉, final_answer를 선택했다면, 이미 답변 작성을 마친 상태여야 합니다.
                    2. "tool" 값이 "search" | "summarize" | "extract_clause"인 경우에는
                    다음 스텝에서 사용할 수 있도록 "tool_input"에 필요한 파라미터들만 넣으세요.

                    [사용자 질문]
                    {user_query}

                    [최근 대화 컨텍스트]
                    {memory_context or "(없음)"}

                    반드시 아래 형식의 JSON만 반환하세요.
                    마크다운 코드 블록(````json` 등)은 절대 포함하지 마세요.

                    예시 1) search를 사용하는 경우 (형식만 참고):
                    {{
                    "tool": "search",
                    "tool_input": {{
                        "query": "연차 사용 규정"
                    }},
                    "reason": "사용자가 연차 사용 규정을 물어보았기 때문에, 우선 관련 규정을 검색한다.",
                    "is_final": false
                    }}

                    예시 2) final_answer를 사용하는 경우 (형식만 참고):
                    {{
                    "tool": "final_answer",
                    "tool_input": {{
                        "answer": "현재 제가 알고 있는 규정은 휴가 규정, 재택근무 규정, 보안 규정입니다. 각각의 규정은 다음과 같은 내용을 담고 있습니다: ... (중략) ..."
                    }},
                    "reason": "검색된 규정 목록과 기존 컨텍스트를 바탕으로 사용자의 질문에 직접 답변할 수 있기 때문에 최종 답변을 생성한다.",
                    "is_final": true
                    }}
                """.strip()

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

        # 필수 필드 기본값 보정
        plan.setdefault("tool", "search")
        plan.setdefault("tool_input", {})
        plan.setdefault("reason", "")
        plan.setdefault("is_final", False)

        # final_answer용 추가 보정:
        # LLM이 규칙을 어기고 answer를 안 넣었거나 비어있을 때 안전하게 기본 답변 채우기
        if plan["tool"] == "final_answer":
            tool_input = plan.get("tool_input") or {}
            answer = tool_input.get("answer")

            if not isinstance(answer, str) or not answer.strip():
                # 기본 fallback 답변
                tool_input["answer"] = (
                    "현재까지 수집한 정보만으로는 질문에 대한 구체적인 규정 설명을 만들지 못했습니다. "
                    "예를 들어 '연차 규정 알려줘', '재택근무 규정 알려줘', '보안 규정 알려줘'처럼 "
                    "원하시는 규정 종류나 상황을 조금 더 구체적으로 말해주시면, 해당 규정을 기준으로 자세히 답변해 줄 수 있습니다."
                )
                plan["tool_input"] = tool_input

        return plan
