from typing import Dict, Any, List

from app.agent.tools import SearchTool, SummarizeTool, ClauseTool


class Executor:
    """
    Planner가 내린 계획에 따라 실제 Tool을 실행하는 모듈.
    """

    def __init__(self, search_tool: SearchTool, summarize_tool: SummarizeTool, clause_tool: ClauseTool):
        self.search_tool = search_tool
        self.summarize_tool = summarize_tool
        self.clause_tool = clause_tool

    def execute(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        tool = plan.get("tool")
        tool_input = plan.get("tool_input") or {}
        result: Any = None

        if tool == "search":
            query = tool_input.get("query", user_query)
            result = self.search_tool.run(query=query)
        elif tool == "summarize":
            docs: List[str] = tool_input.get("texts", [])
            if not docs:
                result = "summarize 할 텍스트가 없습니다."
            else:
                result = self.summarize_tool.run(texts=docs, user_query=user_query)
        elif tool == "extract_clause":
            docs: List[str] = tool_input.get("texts", [])
            if not docs:
                result = "추출할 규정 텍스트가 없습니다."
            else:
                result = self.clause_tool.run(texts=docs, user_query=user_query)
        elif tool == "final_answer":
            # final_answer는 executor에서 별도 처리 없이 plan 자체에 들어있다고 가정할 수도 있음.
            result = tool_input.get("answer", "별도의 최종 답변이 제공되지 않았습니다.")
        else:
            result = f"알 수 없는 tool: {tool}"

        return {
            "tool": tool,
            "tool_input": tool_input,
            "output": result,
            "reason": plan.get("reason", ""),
            "is_final": plan.get("is_final", False),
        }
