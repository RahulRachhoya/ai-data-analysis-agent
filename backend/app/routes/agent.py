import json
import asyncio
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import AgentQueryRequest
from app.services.data_loader import get_dataset_info
from app.agents.graph import get_agent

router = APIRouter(prefix="/api/agent", tags=["agent"])


async def stream_agent_response(
    question: str, dataset_id: str
) -> AsyncGenerator[str, None]:
    """Run the agent and stream SSE events as it progresses through each step."""

    def _emit(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # Emit heartbeat to keep connection alive
    yield _emit("heartbeat", {})

    # Load dataset info
    info = get_dataset_info(dataset_id)
    if not info:
        yield _emit("error", {"message": f"Dataset {dataset_id} not found"})
        return

    # Prepare initial state
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "dataset_id": dataset_id,
        "dataset_file_path": info["file_path"],
        "dataset_info": info,
        "user_question": question,
        "error_count": 0,
        "errors": [],
    }

    agent = get_agent()

    try:
        # Run the agent graph step by step
        step_events = {
            "analyze_schema": ("thinking", {"step": "analyzing", "message": "📊 Analyzing your dataset schema..."}),
            "plan_analysis": ("thinking", {"step": "planning", "message": "🧠 Planning the analysis approach..."}),
            "generate_code": ("thinking", {"step": "coding", "message": "✍️ Writing Python analysis code..."}),
            "execute_code": ("thinking", {"step": "executing", "message": "🚀 Running analysis in sandbox..."}),
        }

        async for event in agent.astream_events(initial_state, config, version="v1"):
            event_type = event.get("event", "")
            name = event.get("name", "")

            # Emit step events
            if event_type == "on_chain_start" and name in step_events:
                evt, data = step_events[name]
                yield _emit(evt, data)

            # Emit the generated code when it's created
            if name == "generate_code" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                code = output.get("generated_code", "")
                if code:
                    yield _emit("code", {"code": code, "language": "python"})

            # Emit execution results
            if name == "execute_code" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                result = output.get("execution_result", {})
                if result.get("plots"):
                    for plot in result["plots"]:
                        yield _emit("plot", plot)
                if result.get("plotly_figures"):
                    for fig in result["plotly_figures"]:
                        yield _emit("plot", {"type": "plotly", "figure": fig})
                if result.get("stdout"):
                    yield _emit("stdout", {"text": "\n".join(result["stdout"])})
                if result.get("error"):
                    yield _emit("error", {
                        "message": result["error"].get("value", "Execution error"),
                    })

            # Emit errors during retry
            if name == "fix_error" and event_type == "on_chain_start":
                yield _emit("thinking", {
                    "step": "fixing",
                    "message": "🔧 Fixing code errors and retrying...",
                })

            # Emit final response
            if name == "synthesize" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                response_text = output.get("final_response", "")
                if response_text:
                    yield _emit("message", {"content": response_text})
                yield _emit("done", {})

    except Exception as e:
        yield _emit("error", {"message": f"Agent error: {str(e)}"})
        yield _emit("done", {})


@router.post("/query")
async def query_agent(request: AgentQueryRequest):
    """Send a query to the data analysis agent with SSE streaming."""
    info = get_dataset_info(request.dataset_id)
    if not info:
        raise HTTPException(404, f"Dataset {request.dataset_id} not found")

    return StreamingResponse(
        stream_agent_response(request.question, request.dataset_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
