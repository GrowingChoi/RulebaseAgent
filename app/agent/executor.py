# app/agent/executor.py
from __future__ import annotations

from typing import Dict, Any

from app.agent.tools.base import Tool


class Executor:
    def __init__(self, tool_registry: Dict[str, Tool]):
        self.tool_registry = tool_registry

    def execute(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:        
        tool_name: str = plan.get("tool", "")
        tool_input: Dict[str, Any] = plan.get("tool_input", {}) or {}
        
        if tool_name == "final_answer":
            result = tool_input.get("answer", "별도의 최종 답변이 제공되지 않았습니다.")
            is_final = True

        else:
            tool = self.tool_registry.get(tool_name)
            if tool is None:
                result = f"알 수 없는 tool: {tool_name}"
                is_final = True  # 더 진행해봐야 의미 없으니 종료
            else:
                try:
                    result = tool.run(user_query=user_query, tool_input=tool_input)
                except Exception as e:
                    result = {"error": f"'{tool_name}' 실행 중 오류 발생: {e}"}
        return {
            "tool": tool_name,
            "tool_input": tool_input,
            "output": result,
            "reason": plan.get("reason", ""),
            "is_final": is_final,
        }
