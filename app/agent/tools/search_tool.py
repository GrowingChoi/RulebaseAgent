import json
import os
from typing import List, Dict


class SearchTool:
    """
    규정(rule) 텍스트에 대해 간단한 키워드 기반 검색을 수행하는 Tool.
    실제 서비스에서는 Qdrant, Elasticsearch 등으로 교체 가능.
    """

    name = "search"

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict]:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"규정 데이터 파일을 찾을 수 없습니다: {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        매우 단순한 키워드 매칭 기반 검색.
        """
        query_lower = query.lower()
        scored = []
        for rule in self.rules:
            text = (rule["title"] + " " + rule["content"]).lower()
            score = sum(query_lower.count(token) for token in query_lower.split())
            if score > 0:
                scored.append((score, rule))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]
        return results
