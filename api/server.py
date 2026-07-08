"""
Atlas OS - API Server (FastAPI)

This exposes Atlas OS as a service:
- Run goals via HTTP
- Retrieve execution results
- Inspect system status
"""

from fastapi import FastAPI
from pydantic import BaseModel

from core.executive_ai import ExecutiveAI

app = FastAPI(title="Atlas OS API", version="1.0")

executive = ExecutiveAI()

class GoalRequest(BaseModel):
    goal: str

@app.get("/")
def root():
    return {"status": "Atlas OS API running"}

@app.post("/run")
def run_goal(req: GoalRequest):
    return executive.run_goal(req.goal)

@app.get("/memory")
def get_memory():
    return executive.memory.data

@app.get("/history")
def get_history():
    return [t.to_dict() for t in executive.task_history]