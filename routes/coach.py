from fastapi import APIRouter , UploadFile, File
from pydantic import BaseModel
import shutil

from agent.coach import run_agent
from rag.chunking import ingest_document

router = APIRouter(prefix="/coach",tags=["Coach"])

session = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/start-session")
def start_session():
    session_id = f"session_{len(session) + 1}"
