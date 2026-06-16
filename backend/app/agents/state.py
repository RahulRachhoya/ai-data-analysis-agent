from typing import Annotated, TypedDict, Dict, List, Optional
from operator import add
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the data analysis agent graph. Extended for multi-agent orchestration:
    - current_agent / agent_statuses / agent_messages for comms + heartbeats (research-backed supervisor pattern).
    - waiting_for for explicit waits (one agent waits for another\'s response via state flags).
    - suggestions + step_by_step_narrative for UX (dataset suggestions, step-by-step answers).
    Reuse existing messages reducer for comms history.
    """

    # Chat history (managed by LangGraph) - reused for inter-agent messages too
    messages: Annotated[list[BaseMessage], add_messages]

    # Dataset information
    dataset_id: str
    dataset_file_path: str
    dataset_info: dict

    # Analysis workflow
    user_question: str
    analysis_plan: str
    generated_code: str
    execution_result: dict

    # Error handling
    error_count: int
    errors: list[str]

    # Output
    final_response: str
    plots: list[dict]
    plotly_figures: list[dict]

    # === Multi-agent orchestration extensions ===
    # Current active agent (for supervisor + status)
    current_agent: Optional[str]

    # Per-agent status for heartbeats/liveness (e.g. {"profiler": "working", "suggester": "waiting"})
    # Updated by agents on start/end; supervisor "listens"; emitted via SSE heartbeats.
    agent_statuses: Dict[str, str]

    # Inter-agent communication (tagged messages; agents append, others listen/read in prompts/state)
    # Format example: [{"from": "supervisor", "to": "executor", "content": "...", "type": "task|response|heartbeat", "ts": ...}]
    agent_messages: List[dict]

    # Explicit wait coordination: e.g. {"executor": ["profiler_done"]} 
    # One agent waits for flags set by producers (conditional edges check this).
    waiting_for: Dict[str, List[str]]

    # Dataset suggestions (from Suggester agent; proactive "do more with dataset")
    suggestions: List[str]

    # Built step-by-step narrative (for final user-facing step-by-step answers)
    step_by_step_narrative: str
