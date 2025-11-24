# RulebaseAgent

규정(rule) 텍스트를 대상으로 Tool-Using Agent 구조를 실험하기 위한 미니 프로젝트입니다.

## 실행 방법

```bash
# 1) 가상환경 생성 후
pip install -r requirements.txt

# 2) OPENAI_API_KEY 설정
export OPENAI_API_KEY="YOUR_KEY_HERE"  # Windows면 set 혹은 PowerShell $env:OPENAI_API_KEY

# 3) 서버 실행
uvicorn app.main:app --reload
```

브라우저에서 http://127.0.0.1:8000/docs 접속 후
POST /agent 엔드포인트로 질의할 수 있습니다.