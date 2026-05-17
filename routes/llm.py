from fastapi import APIRouter
from pydantic import BaseModel
from services.llm import call_llm

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/ask")
def ask_llm(request: PromptRequest):
    response = call_llm(request.prompt)
    return {"response": response}