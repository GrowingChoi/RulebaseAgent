# app/main.py
import os
from typing import List, Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agent.memory import ConversationMemory
from app.agent.planner import Planner
from app.agent.executor import Executor
from app.agent.tools import build_tool_registry, Tool


# FastAPI 앱 생성
app = FastAPI(
    title="RulebaseAgent API",
    version="0.2.0",
    description="규정 기반 Tool-Using Agent 데모 API (리팩토링 버전)",
)

# 도구 및 코어 컴포넌트 초기화

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app 디렉토리
DATA_PATH = os.path.join(BASE_DIR, "data", "rules_sample.json")

tool_registry: Dict[str, Tool] = build_tool_registry(data_path=DATA_PATH)

# LLM 플래너에게 알려줄 tool 이름들 + pseudo-tool "final_answer"
tool_names = list(tool_registry.keys()) + ["final_answer"]

planner = Planner(tool_names=tool_names)
executor = Executor(tool_registry=tool_registry)
memory = ConversationMemory(max_turns=5)


# Request / Response 모델 정의

class AgentRequest(BaseModel):
    query: str
    max_steps: int = 3


class PlanStep(BaseModel):
    tool: str
    tool_input: Dict[str, Any]
    output: Any
    reason: str
    is_final: bool


class AgentResponse(BaseModel):
    query: str
    steps: List[PlanStep]
    final_answer: str


@app.post("/agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """
    사용자의 query를 받아 Planner → Executor → Memory를 거치는 Agent 루프를 수행하고,
    각 step과 최종 답변을 반환.
    """
    try:
        user_query = request.query
        max_steps = request.max_steps

        steps: List[PlanStep] = []

        # multi-step loop
        current_context = memory.get_context_str()
        last_result: Any = None

        for _ in range(max_steps):
            # 1) Plan
            plan = planner.plan(user_query=user_query, memory_context=current_context)

            # 2) search → summarize / extract_clause 연결
            if last_result is not None and isinstance(last_result, list):
                if plan.get("tool") in ("summarize", "extract_clause"):
                    texts = [item.get("content", "") for item in last_result]
                    plan.setdefault("tool_input", {})
                    plan["tool_input"].setdefault("texts", texts)

            # 3) Execute
            exec_result = executor.execute(plan=plan, user_query=user_query)

            step = PlanStep(
                tool=exec_result["tool"],
                tool_input=exec_result["tool_input"],
                output=exec_result["output"],
                reason=exec_result["reason"],
                is_final=exec_result["is_final"],
            )
            steps.append(step)

            last_result = exec_result["output"]

            # 4) 종료 조건
            if exec_result["is_final"] or exec_result["tool"] == "final_answer":
                break

            # (원하면 여기서 current_context를 last_result 기반으로 업데이트하도록 확장 가능)
            current_context = memory.get_context_str()

        # 최종 답변 결정 로직
        if isinstance(last_result, list):
            # search 결과만 남아있는 경우 → 한 번 더 summarize 해서 마무리
            texts = [item.get("content", "") for item in last_result]

            summarize_tool = tool_registry.get("summarize")
            if summarize_tool is not None:
                summarized = summarize_tool.run(
                    user_query=user_query,
                    tool_input={"texts": texts},
                )

                summary_step = PlanStep(
                    tool="summarize (post-processing)",
                    tool_input={"texts": texts},
                    output=summarized,
                    reason="search 결과를 바탕으로 최종 사용자 답변을 생성",
                    is_final=True,
                )
                steps.append(summary_step)
                final_answer = summarized
            else:
                final_answer = str(last_result)
        else:
            final_answer = (
                str(last_result) if last_result is not None else "답변을 생성하지 못했습니다."
            )

        # 메모리에 저장
        memory.add_turn(user=user_query, agent=final_answer)

        return AgentResponse(
            query=user_query,
            steps=steps,
            final_answer=final_answer,
        )

    except Exception as e:
        # 터미널에도 로깅
        print("/agent 내부 에러 발생:", repr(e))
        # 클라이언트에도 에러 메시지 전달
        raise HTTPException(status_code=500, detail=str(e))

# app/main.py 맨 아래 근처에 추가

@app.get("/ping")
async def ping():
    return {"status": "ok"}
