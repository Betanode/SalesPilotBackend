import uuid
from typing import Dict
from agent.coach import AgentState

sessions: Dict[str, AgentState] = {}


def create_session() -> tuple[str, AgentState]:
    session_id = str(uuid.uuid4())
    state: AgentState = {
        "messages": [],
        "turn": 0,
        "feedbacks": [],
        "done": False
    }
    sessions[session_id] = state
    return session_id, state


def get_session(session_id: str) -> AgentState:
    if session_id not in sessions:
        raise KeyError(f"Session '{session_id}' not found.")
    return sessions[session_id]


def update_session(session_id: str, state: AgentState):
    sessions[session_id] = state


def delete_session(session_id: str):
    sessions.pop(session_id, None)