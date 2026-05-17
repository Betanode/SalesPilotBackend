from typing import TypedDict, List, Dict
from services.llm import call_llm
from rag.chunking import hybrid_retrieve


class AgentState(TypedDict):
    messages: List[Dict]
    turn: int
    feedbacks: List[str]
    done: bool


def format_messages(messages: List[Dict]) -> str:
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])


def ask_question(state: AgentState) -> AgentState:
    state["messages"].append({
        "role": "assistant",
        "content": "Hello! I am your sales coach. Please tell me about the product you want to sell and what aspect of the sales conversation you'd like to practice today."
    })
    return state


def generate_response(state: AgentState) -> AgentState:
    last_user_message = state["messages"][-1]["content"]

    chunks = hybrid_retrieve(last_user_message, k=5)
    context = "\n".join([c["content"] for c in chunks]) if chunks else "No product context available."

    prompt = f"""You are an expert sales coach conducting a practice interview with a sales representative.

Conversation so far:
{format_messages(state["messages"])}

Relevant product knowledge from the uploaded document:
{context}

Your task:
1. Give short, specific, actionable feedback on the sales rep's last answer (2-3 sentences max).
2. Ask one focused follow-up question to probe their sales skills deeper.

Use EXACTLY this format and nothing else:

FEEDBACK:
<your feedback here>

QUESTION:
<your next question here>
"""

    response = call_llm(prompt)
    feedback, question = parse_llm_response(response)

    state["feedbacks"].append(feedback)
    state["messages"].append({
        "role": "assistant",
        "content": question
    })

    state["turn"] += 1
    return state


def final_feedback(state: AgentState) -> AgentState:
    all_feedbacks = "\n".join(
        [f"Turn {i+1}: {fb}" for i, fb in enumerate(state["feedbacks"])]
    )

    prompt = f"""You are a professional sales coach. A sales rep just completed a practice session.

Here is the turn-by-turn feedback from the session:
{all_feedbacks}

Generate a structured final performance report with these exact sections:

STRENGTHS:
- List what the rep did well

WEAKNESSES:
- List areas that need improvement

KEY IMPROVEMENTS:
- List 2-3 specific, actionable things to work on

FINAL SCORE: X/10
(with one sentence justifying the score)
"""

    summary = call_llm(prompt)
    state["messages"].append({
        "role": "assistant",
        "content": summary
    })
    state["done"] = True
    return state


def parse_llm_response(text: str):
    try:
        parts = text.split("QUESTION:")
        feedback = parts[0].replace("FEEDBACK:", "").strip()
        question = parts[1].strip()
        return feedback, question
    except Exception:
        return text.strip(), "Can you elaborate on that point a bit more?"