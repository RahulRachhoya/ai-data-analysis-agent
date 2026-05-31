from typing import Annotated, TypedDict
from operator import add
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the data analysis agent graph."""

    # Chat history (managed by LangGraph)
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
