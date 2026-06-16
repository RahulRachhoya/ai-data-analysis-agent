import json
import asyncio
import uuid
import time
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
    """Run the (now multi-agent) orchestration and stream SSE events.
    Enhanced for step-by-step (plan + narrative), suggestions, agent heartbeats/status (from multi-agent comms),
    and waiting visibility. Periodic heartbeats emitted even during long specialist work (LLM/sandbox).
    Backward compatible (old events still emitted; new ones additive).
    """

    def _emit(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # Emit initial heartbeat + multi-agent start status
    yield _emit("heartbeat", {"agent_statuses": {"supervisor": "orchestrating"}})

    # Load dataset info
    info = get_dataset_info(dataset_id)
    if not info:
        yield _emit("error", {"message": f"Dataset {dataset_id} not found"})
        return

    # Prepare initial state (extended for multi-agent)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "dataset_id": dataset_id,
        "dataset_file_path": info["file_path"],
        "dataset_info": info,
        "user_question": question,
        "error_count": 0,
        "errors": [],
        "current_agent": "supervisor",
        "agent_statuses": {"supervisor": "starting"},
        "agent_messages": [],
        "waiting_for": {},
        "suggestions": [],
        "step_by_step_narrative": "",
    }

    agent = get_agent()

    heartbeat_interval = 3.0  # seconds; configurable via ma-8 later
    last_heartbeat = time.time()

    try:
        # Run the multi-agent graph (supervisor drives specialists with comms/waits/heartbeats in state)
        async for event in agent.astream_events(initial_state, config, version="v1"):
            event_type = event.get("event", "")
            name = event.get("name", "")
            output = event.get("data", {}).get("output", {}) if event_type == "on_chain_end" else {}

            # Periodic transport-level heartbeat (even if no graph event; agents update status in state)
            now = time.time()
            if now - last_heartbeat > heartbeat_interval:
                current_status = output.get("agent_statuses") or initial_state.get("agent_statuses", {})
                yield _emit("heartbeat", {"ts": now, "agent_statuses": current_status, "note": "multi-agent liveness (supervisor listening)"})
                last_heartbeat = now

            # Emit step / agent status events (from supervisor/specialists)
            if event_type == "on_chain_start":
                if name == "supervisor":
                    yield _emit("thinking", {"step": "orchestrating", "message": "\ud83e\udde0 Supervisor coordinating multi-agents (listening for heartbeats/responses)..."})
                elif name in ["profiler", "planner", "coder", "executor", "critic", "suggester", "presenter"]:
                    yield _emit("thinking", {"step": name, "message": f"\ud83e\udd16 {name.capitalize()} agent active (heartbeat updated)"})

            # Richer per-agent events from state updates (plan, suggestions, status)
            if event_type == "on_chain_end":
                # Plan exposure (step-by-step)
                if name == "planner" and output.get("analysis_plan"):
                    yield _emit("plan", {"plan": output["analysis_plan"], "message": "Detailed step-by-step plan from Planner agent"})
                # Suggestions (dataset-specific "do more")
                if name in ["suggester", "presenter"] and output.get("suggestions"):
                    yield _emit("suggestions", {"suggestions": output["suggestions"], "message": "Agent-suggested next actions for this dataset"})
                # Agent status/heartbeat from multi-agent comms
                if output.get("agent_statuses"):
                    yield _emit("agent_status", {"statuses": output["agent_statuses"], "current": output.get("current_agent")})
                # Code (internal; emitted for debug but presenter de-emphasizes in final per req)
                if name == "coder" and output.get("generated_code"):
                    yield _emit("code", {"code": output["generated_code"], "language": "python", "note": "Internal - executor will compile/run; not primary user output"})
                # Execution results (now from Executor specialist; primary)
                if name == "executor" and output.get("execution_result"):
                    res = output["execution_result"]
                    if res.get("plots"):
                        for plot in res["plots"]:
                            yield _emit("plot", plot)
                    if res.get("plotly_figures"):
                        for fig in res["plotly_figures"]:
                            yield _emit("plot", {"type": "plotly", "figure": fig})
                    if res.get("stdout"):
                        yield _emit("stdout", {"text": "\n".join(res["stdout"])})
                    if res.get("error"):
                        yield _emit("error", {"message": res["error"].get("value", "Execution error from Executor")})
                # Final step-by-step + suggestions (presenter focuses execution/insights)
                if name == "presenter" and output.get("final_response"):
                    yield _emit("message", {"content": output["final_response"]})
                    yield _emit("done", {})

            # Legacy thinking for compat (coarse steps)
            if event_type == "on_chain_start" and name in ["analyze_schema", "plan_analysis", "generate_code", "execute_code"]:
                # Map legacy to new specialist names where possible
                legacy_map = {"analyze_schema": "profiler", "plan_analysis": "planner", "generate_code": "coder", "execute_code": "executor"}
                mapped = legacy_map.get(name, name)
                yield _emit("thinking", {"step": mapped, "message": f"Legacy-mapped {name} \u2192 {mapped} specialist"})

            # Crit/fix legacy
            if name == "fix_error" or (name == "critic" and event_type == "on_chain_start"):
                yield _emit("thinking", {"step": "fixing", "message": "\ud83d\udd27 Critic/Fixer reviewing (communicating with executor)"})

    except Exception as e:
        yield _emit("error", {"message": f"Multi-agent orchestration error: {str(e)}"})
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
