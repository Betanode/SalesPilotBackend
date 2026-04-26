from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from services.llm import call_llm
from rag.chunking import hybrid_retrieve



class AgentState(TypedDict):
    messages: List[Dict]
    turn: int
    feedbacks: List[str]
    done: bool



def format_messages(messages: List[Dict]) -> str:
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])



def ask_question(state: AgentState):
    """
    Only ask first question
    """
    if state["turn"] == 0:
        state["messages"].append({
            "role": "assistant",
            "content": "Hello! What would you like to discuss today?"
        })
    return state



def generate_response(state: AgentState):

    last_user_message = state["messages"][-1]["content"]

    chunks = hybrid_retrieve(last_user_message, k=5)
    context = "\n".join([c["content"] for c in chunks])

    prompt = f"""
You are an expert sales coach.

Conversation so far:
{format_messages(state["messages"])}

Relevant knowledge:
{context}

Task:
1. Give short, actionable feedback on user's last answer
2. Ask next better question to improve skill

STRICT FORMAT:
FEEDBACK:
<feedback>

QUESTION:
<next question>
"""

    response = call_llm(prompt)
    feedback, question = parse_llm_response(response)

    # store feedback separately
    state["feedbacks"].append(feedback)

    # ONLY question goes to chat
    state["messages"].append({
        "role": "assistant",
        "content": question
    })

    state["turn"] += 1
    return state



def check_end(state: AgentState):
    if state["turn"] >= 10:
        state["done"] = True
    return state



def final_feedback(state: AgentState):

    all_feedbacks = "\n".join(state["feedbacks"])

    prompt = f"""
You are a professional sales coach.

Based on the feedback below, generate a structured report.

{all_feedbacks}

Include:
- Strengths
- Weaknesses
- Improvements
- Final Score out of 10
"""

    summary = call_llm(prompt)

    state["messages"].append({
        "role": "assistant",
        "content": summary
    })

    return state



def parse_llm_response(text: str):

    try:
        parts = text.split("QUESTION:")
        feedback = parts[0].replace("FEEDBACK:", "").strip()
        question = parts[1].strip()
    except Exception:
        feedback = text.strip()
        question = "Can you explain more?"

    return feedback, question



def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("ask", ask_question)
    builder.add_node("generate", generate_response)
    builder.add_node("check", check_end)
    builder.add_node("summary", final_feedback)

    builder.set_entry_point("ask")

    builder.add_edge("ask", "generate")
    builder.add_edge("generate", "check")

    def should_end(state: AgentState):
        return "end" if state["done"] else "continue"

    builder.add_conditional_edges(
        "check",
        should_end,
        {
            "continue": "generate",
            "end": "summary"
        }
    )

    builder.add_edge("summary", END)

    return builder.compile()



graph = build_graph()


def run_agent(state: AgentState):
    return graph.invoke(state)