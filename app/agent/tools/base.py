from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class Tool(ABC):
    """
    모든 Tool이 따라야 하는 공통 인터페이스.

    - name: planner가 선택할 때 사용할 문자열 이름
    - description: 프롬프트/문서화용 설명
    - run(): 실제 실행 로직 (user_query + tool_input 기반)
    """

    name: str
    description: str = ""

    @abstractmethod
    def run(self, *, user_query: str, tool_input: Dict[str, Any]) -> Any:
        """
        Tool 실행 메서드.
        - param user_query: 원본 사용자 질문
        - param tool_input: planner가 넘겨준 세부 입력 파라미터
        - return: Tool 실행 결과
        """
        raise NotImplementedError
