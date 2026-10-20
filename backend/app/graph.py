"""SmartTask AI - LangGraph workflow.

START -> extract_tasks -> prioritize_tasks -> format_results -> END
"""
import os
from typing import List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from .schemas import ExtractionResult, PrioritizationResult

load_dotenv()

PRIORITY_ORDER = ["High", "Medium", "Low"]
PRIORITY_ICON = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}


class TaskState(TypedDict, total=False):
    """Shared state passed from node to node."""
    user_input: str          # raw natural-language message
    extracted: List[dict]    # output of Node 1
    prioritized: List[dict]  # output of Node 2
    output: str              # output of Node 3 (readable list)


def _get_llm() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. Create backend/.env from .env.example "
            "and add your Gemini API key."
        )
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        google_api_key=api_key,
        temperature=0,
    )


# --------------------------------------------------------------------------
# Node 1 - Task extraction
# --------------------------------------------------------------------------
EXTRACT_PROMPT = (
    "You are a task extraction assistant. The user writes informally about "
    "things they need to do. Split the message into individual, separate "
    "tasks. Keep each title short and action-oriented. Copy any deadline or "
    "time phrase the user mentioned (today, tomorrow, next week...). "
    "Do not invent tasks that are not in the message."
)


def extract_tasks(state: TaskState) -> TaskState:
    llm = _get_llm().with_structured_output(ExtractionResult)
    result: ExtractionResult = llm.invoke(
        [SystemMessage(content=EXTRACT_PROMPT),
         HumanMessage(content=state["user_input"])]
    )
    return {"extracted": [t.model_dump() for t in result.tasks]}


# --------------------------------------------------------------------------
# Node 2 - Task prioritization
# --------------------------------------------------------------------------
PRIORITIZE_PROMPT = (
    "You are a productivity coach. For each task assign a priority: "
    "High (urgent: due today/tomorrow or very important), "
    "Medium (due within about a week or moderately important), "
    "Low (no near deadline or optional). Use the deadline as the main "
    "signal. Return every task you receive, keep the titles and deadlines "
    "unchanged, and add a one-sentence reason."
)


def prioritize_tasks(state: TaskState) -> TaskState:
    if not state.get("extracted"):
        return {"prioritized": []}
    llm = _get_llm().with_structured_output(PrioritizationResult)
    task_lines = "\n".join(
        f"- {t['title']} (deadline: {t.get('deadline') or 'not specified'})"
        for t in state["extracted"]
    )
    result: PrioritizationResult = llm.invoke(
        [SystemMessage(content=PRIORITIZE_PROMPT),
         HumanMessage(content=task_lines)]
    )
    return {"prioritized": [t.model_dump() for t in result.tasks]}


# --------------------------------------------------------------------------
# Node 3 - Format results (plain Python, no LLM call needed)
# --------------------------------------------------------------------------
def format_results(state: TaskState) -> TaskState:
    tasks = state.get("prioritized", [])
    if not tasks:
        return {"output": "No tasks were found in your message."}

    lines = ["YOUR ORGANIZED TO-DO LIST", "=" * 28]
    for level in PRIORITY_ORDER:
        group = [t for t in tasks if t["priority"] == level]
        if not group:
            continue
        lines.append(f"\n{PRIORITY_ICON[level]} {level.upper()} PRIORITY")
        for i, t in enumerate(group, 1):
            due = f" (due: {t['deadline']})" if t.get("deadline") else ""
            lines.append(f"  {i}. {t['title']}{due}")
            lines.append(f"     - {t['reason']}")
    return {"output": "\n".join(lines)}


# --------------------------------------------------------------------------
# Graph wiring
# --------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(TaskState)
    graph.add_node("extract_tasks", extract_tasks)
    graph.add_node("prioritize_tasks", prioritize_tasks)
    graph.add_node("format_results", format_results)

    graph.add_edge(START, "extract_tasks")
    graph.add_edge("extract_tasks", "prioritize_tasks")
    graph.add_edge("prioritize_tasks", "format_results")
    graph.add_edge("format_results", END)
    return graph.compile()


workflow = build_graph()


def organize(message: str) -> TaskState:
    """Run the full workflow for one user message."""
    return workflow.invoke({"user_input": message})
