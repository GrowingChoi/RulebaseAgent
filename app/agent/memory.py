from typing import List, Dict


class ConversationMemory:
    """
    간단한 in-memory 대화 메모리.
    실제 서비스에서는 Redis/DB 등으로 교체 가능.
    """

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._history: List[Dict[str, str]] = []

    def add_turn(self, user: str, agent: str) -> None:
        self._history.append({"user": user, "agent": agent})
        if len(self._history) > self.max_turns:
            self._history = self._history[-self.max_turns :]

    def get_context_str(self) -> str:
        """
        LLM 프롬프트에 주입할 문자열 형태의 최근 대화 컨텍스트.
        """
        if not self._history:
            return ""
        lines = []
        for turn in self._history:
            lines.append(f"사용자: {turn['user']}")
            lines.append(f"에이전트: {turn['agent']}")
        return "\n".join(lines)
