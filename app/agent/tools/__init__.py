# app/agent/tools/__init__.py
from typing import Dict

from .base import Tool
from .search_tool import SearchTool
from .summarize_tool import SummarizeTool
from .clause_tool import ClauseTool


def build_tool_registry(*, data_path: str) -> Dict[str, Tool]:
    """
    프로젝트에서 사용할 Tool 인스턴스를 생성하고
    `{tool_name: tool_instance}` 형태의 레지스트리를 만들어 반환.

    새 Tool을 추가하고 싶으면 여기에서만 인스턴스를 추가해도 됨.
    """
    search_tool = SearchTool(data_path=data_path)
    summarize_tool = SummarizeTool()
    clause_tool = ClauseTool()

    tools = [search_tool, summarize_tool, clause_tool]
    return {tool.name: tool for tool in tools}


__all__ = [
    "Tool",
    "SearchTool",
    "SummarizeTool",
    "ClauseTool",
    "build_tool_registry",
]
