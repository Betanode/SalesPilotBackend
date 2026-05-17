from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.coach import ask_question, generate_response, final_feedback
from services.session import create_session, get_session, update_session, delete_session

router = APIRouter()

MAX_TURNS = 10


class MessageRequest(BaseModel):
    session_id: str
    message: str


@router.post("/session/start")
async def start_session():
    """
    Creates a new coaching session and returns the opening message from the agent.
    Call this once before sending any messages.
    """
    session_id, state = create_session()
    state = ask_question(state)
    update_session(session_id, state)

    return {
        "session_id": session_id,
        "message": state["messages"][-1]["content"],
        "turn": state["turn"],
        "is_final": False
    }


@router.post("/session/message")
async def send_message(request: MessageRequest):
    """
    Send the user's reply and get the agent's next question.
    When turn reaches MAX_TURNS, returns the final performance report instead.
    """
    try:
        state = get_session(request.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found. Please start a new session.")

    if state["done"]:
        raise HTTPException(status_code=400, detail="This session is already complete.")

    state["messages"].append({"role": "user", "content": request.message})

    if state["turn"] >= MAX_TURNS:
        state = final_feedback(state)
        update_session(request.session_id, state)
        return {
            "message": state["messages"][-1]["content"],
            "turn": state["turn"],
            "is_final": True
        }

    state = generate_response(state)
    update_session(request.session_id, state)

    return {
        "message": state["messages"][-1]["content"],
        "turn": state["turn"],
        "is_final": False
    }


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    Explicitly delete a session to free memory.
    """
    delete_session(session_id)
    return {"message": "Session ended."}