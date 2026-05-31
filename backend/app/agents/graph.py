from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState
from app.agents.nodes import (
    analyze_schema_node,
    plan_analysis_node,
    generate_code_node,
    execute_code_node,
    fix_error_node,
    synthesize_node,
)
from app.config import MAX_RETRIES


def should_retry(state: AgentState) -> str:
    """Determine whether to retry code execution or synthesize the response."""
    execution_result = state.get("execution_result", {})
    error = execution_result.get("error")
    error_count = state.get("error_count", 0)

    if error and error_count < MAX_RETRIES:
        return "fix_error"
    return "synthesize"


def build_agent_graph() -> StateGraph:
    """Build and return the LangGraph agent graph."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_schema", analyze_schema_node)
    workflow.add_node("plan_analysis", plan_analysis_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("fix_error", fix_error_node)
    workflow.add_node("synthesize", synthesize_node)

    # Set entry point
    workflow.set_entry_point("analyze_schema")

    # Add edges
    workflow.add_edge("analyze_schema", "plan_analysis")
    workflow.add_edge("plan_analysis", "generate_code")
    workflow.add_edge("generate_code", "execute_code")

    # Conditional edge: retry or synthesize
    workflow.add_conditional_edges(
        "execute_code",
        should_retry,
        {
            "fix_error": "fix_error",
            "synthesize": "synthesize",
        },
    )

    # Loop back from fix_error to execute_code
    workflow.add_edge("fix_error", "execute_code")

    # End after synthesis
    workflow.add_edge("synthesize", END)

    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# Singleton
agent_app = None


def get_agent():
    """Get or create the agent graph."""
    global agent_app
    if agent_app is None:
        agent_app = build_agent_graph()
    return agent_app
