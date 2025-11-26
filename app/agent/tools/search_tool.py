# app/agent/tools/search_tool.py
import json
import os
from typing import List, Dict, Any

from .base import Tool


class SearchTool(Tool):
    """
    규정(rule) 텍스트에 대해 간단한 키워드 기반 검색을 수행하는 Tool.
    실제 서비스에서는 Qdrant, Elasticsearch 등으로 교체 가능한 위치.
    """

    name = "search"
    description = "규정 텍스트에서 키워드 기반으로 관련 조항을 검색하는 Tool"

    def __init__(self, data_path: str, default_top_k: int = 3) -> None:
        self.data_path = data_path
        self.default_top_k = default_top_k
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"rules 데이터 파일을 찾을 수 없습니다: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("rules 데이터 형식이 올바르지 않습니다. (list[dict] 예상)")

        return data

    def _search(self, *, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        매우 단순한 키워드 매칭 기반 검색.
        """
        query_lower = query.lower()
        scored: List[tuple[int, Dict[str, Any]]] = []

        for rule in self.rules:
            title = str(rule.get("title", ""))
            content = str(rule.get("content", ""))
            text = (title + " " + content).lower()

            score = sum(query_lower.count(token) for token in query_lower.split())
            if score > 0:
                scored.append((score, rule))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]
        return results

    def run(self, *, user_query: str, tool_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tool 인터페이스용 실행 메서드.

        tool_input:
          - query: 검색 키워드 (없으면 user_query 사용)
          - top_k: 검색 개수 (기본 self.default_top_k)
        """
        query = tool_input.get("query") or user_query
        top_k = int(tool_input.get("top_k", self.default_top_k))

        if not query:
            return []

        return self._search(query=query, top_k=top_k)
