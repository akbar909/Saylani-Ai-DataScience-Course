from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.agents.orchestrator import FinanceAgent
from app.api.deps import get_current_user
from app.core.model_registry import ModelRegistry
from app.models.user import User


router = APIRouter(prefix="/agent", tags=["agent"])


class AgentQuestion(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class AgentResponse(BaseModel):
    answer: str
    actions: list[str]


@router.post("/chat", response_model=AgentResponse)
async def chat(payload: AgentQuestion, request: Request, current_user: User = Depends(get_current_user)) -> AgentResponse:
    registry: ModelRegistry = request.app.state.model_registry
    agent = FinanceAgent(registry=registry)
    answer = await agent.answer(payload.message)
    actions = ["view_dashboard"]
    if "forecast" in payload.message.lower():
        actions.append("open_forecast")
    if "fraud" in payload.message.lower() or "risk" in payload.message.lower():
        actions.append("open_fraud")
    return AgentResponse(answer=answer, actions=actions)
