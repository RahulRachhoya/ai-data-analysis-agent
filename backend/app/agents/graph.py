from langgraph.graph import StateGraph, END  # Send for parallel in future (current env may have older langgraph; use sequential handoffs for now)
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState
from app.agents.nodes import (
    # Legacy (for compat/tests)
    analyze_schema_node,
    plan_analysis_node,
    generate_code_node,
    execute_code_node,
    fix_error_node,
    synthesize_node,
    # New multi-agent
    supervisor_node,
    profiler_node,
    planner_node,
    coder_node,
    executor_node,
    critic_node,
    suggester_node,
    presenter_node,
)
from app.config import MAX_RETRIES


def should_retry(state: AgentState) -> str:
    """Determine whether to retry code execution or synthesize the response. (Reused/extended for critic handoff.)"""
    execution_result = state.get("execution_result", {})
    error = execution_result.get("error")
    error_count = state.get("error_count", 0)

    if error and error_count < MAX_RETRIES:
        return "critic"  # multi-agent: handoff to critic instead of simple fix
    return "presenter"  # or supervisor for final


def build_agent_graph() -> StateGraph:
    """Build multi-agent orchestration graph (supervisor + specialists per plan).
    - Supervisor coordinates, listens heartbeats/status, handles waits/comms via state.
    - Specialists communicate (send/listen via agent_messages), update heartbeats/status.
    - Waiting: conditional + waiting_for flags (one waits for another\'s response/flag).
    - Parallel possible via Send for independent (e.g. profiler + initial suggester).
    - Reuses/extends prior single-graph logic + research patterns (LangGraph supervisor, handoffs, group via state).
    """
    workflow = StateGraph(AgentState)

    # Add all nodes (legacy kept for tests/compat; new for orchestration)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("profiler", profiler_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("suggester", suggester_node)
    workflow.add_node("presenter", presenter_node)

    # Legacy nodes (for backward in tests/partial flows)
    workflow.add_node("analyze_schema", analyze_schema_node)
    workflow.add_node("plan_analysis", plan_analysis_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("fix_error", fix_error_node)
    workflow.add_node("synthesize", synthesize_node)

    # Entry: multi-agent supervisor (orchestrates everything, heartbeats, waits)
    workflow.set_entry_point("supervisor")

    # Core multi-agent flow (supervisor routes/handoffs; conditionals for waits/errors)
    # Supervisor decides next (via its logic + state); specialists return control to supervisor for coordination.
    workflow.add_edge("supervisor", "profiler")  # e.g. start with profiling
    workflow.add_edge("profiler", "supervisor")  # report back (comm via state messages/heartbeats)
    workflow.add_edge("supervisor", "planner")
    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("supervisor", "coder")
    workflow.add_edge("coder", "supervisor")
    workflow.add_edge("supervisor", "executor")  # executor "waits" internally via check in node + waiting_for
    workflow.add_edge("executor", "supervisor")

    # Error/critic path (extended should_retry)
    workflow.add_conditional_edges(
        "executor",
        should_retry,
        {
            "critic": "critic",
            "presenter": "supervisor",  # route to suggester/presenter via supervisor
        },
    )
    workflow.add_edge("critic", "supervisor")  # critic reports; supervisor may re-dispatch to executor

    # Suggester (waits on executor via state in its impl); then presenter for final step-by-step + suggestions
    workflow.add_edge("supervisor", "suggester")
    workflow.add_edge("suggester", "supervisor")
    workflow.add_edge("supervisor", "presenter")
    workflow.add_edge("presenter", END)

    # Legacy edges (for compat with old tests/partial calls; single-graph fallback)
    workflow.add_edge("analyze_schema", "plan_analysis")
    workflow.add_edge("plan_analysis", "generate_code")
    workflow.add_edge("generate_code", "execute_code")
    workflow.add_conditional_edges(
        "execute_code",
        should_retry,
        {
            "fix_error": "fix_error",
            "synthesize": "synthesize",
        },
    )
    workflow.add_edge("fix_error", "execute_code")
    workflow.add_edge("synthesize", END)

    # Compile with memory (extended state tracked per thread)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# Singleton (updated name for clarity; get_agent still works)
multi_agent_app = None


def get_agent():
    """Get or create the (now multi-agent) graph. Backward compatible name."""
    global multi_agent_app
    if multi_agent_app is None:
        multi_agent_app = build_agent_graph()
    return multi_agent_app
