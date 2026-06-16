# Multi-Agent Orchestration for Data Analysis Backend

## Overview (per approved plan)
Refactored the prior single LangGraph workflow into a multi-agent system using LangGraph supervisor + specialist pattern (research: LangGraph blogs, AutoGen group chats, CrewAI roles, Semantic Kernel, HearthNet for heartbeats).

**Key changes delivered:**
- Extended AgentState with current_agent, agent_statuses (heartbeats), agent_messages (comms), waiting_for (one waits for response), suggestions (dataset "do more"), step_by_step_narrative.
- Orchestration helpers: update_agent_heartbeat, send_agent_message, check_wait_flags, supervisor_route_decision.
- Specialists (supervisor + profiler, planner, coder (internal), executor (execution/"compile" primary), critic, suggester (dataset suggestions), presenter (step-by-step + insights first)).
- Graph: supervisor entry, handoffs/conditionals for waits/comms, reuse of legacy for compat.
- SSE: periodic heartbeats + new events (plan, suggestions, agent_status); execution results emphasized over raw code.
- Prompts enhanced for step-by-step, suggestions, "wait/listen in state", execution bias.
- Verified locally (state, helpers, specialists, comms/heartbeats/waits/suggestions/narrative).

## Architecture
- **Supervisor**: Orchestrates, listens heartbeats/status (via state), manages waits (flags in waiting_for), routes, builds narrative.
- **Comms**: agent_messages list (tagged from/to/type/content/ts); agents "send" on updates, "listen" via state reads in prompts/state.
- **Heartbeats**: Inter-agent via status + messages (updated on start/end + periodic); transport via SSE timer (emits agent_statuses even during long ops).
- **Waiting**: Producers set "xxx_done" in messages; waiters check via check_wait_flags + conditional edges in supervisor.
- **Step-by-step + Suggestions**: Plan exposed; Suggester (post-executor) generates dataset-specific actions; Presenter structures final as narrative + suggestions (execution/insights dominant; code de-emphasized as "internally compiled by executor").
- **Reuse**: Existing LLM lazy, code guards, sandbox (Executor), data_loader, state messages reducer, MAX_*, tests patterns.

## Flow Example
Supervisor -> Profiler (schema + initial sugs; sends "profiler_done") -> (wait cleared) Planner (step plan) -> Coder (internal code; messages executor) -> Executor (runs sandbox/"compiles"; results primary; messages suggester) -> Suggester (listens results; generates "try group by city...") -> Presenter (step narrative + suggestions) -> Supervisor (final).

Heartbeats emitted throughout; one agent (e.g. executor/suggester) waits for prior via state.

## New/Changed SSE Events (additive)
- heartbeat (now with agent_statuses)
- plan (full from Planner)
- agent_status (from heartbeats/comms)
- suggestions (from Suggester)
- message (now step-by-step narrative + insights + suggestions; code optional/debug)
- (legacy thinking/code/plot/stdout/error/done preserved)

## Next Steps / Future
- Full LLM mocks in tests for end-to-end graph.
- Parallel via Send() for independent agents.
- If distributed: add Redis pubsub for real heartbeats (current is in-graph simulation sufficient for per-query SSE).
- Frontend: consume new events for dedicated "suggestions" UI, richer step timeline.
- Optimize: reuse sandbox across agents in one invocation (current fresh per executor noted as edge).

See approved plan.md for research links, full design, verification steps, and critical files.

This implements the requested multi-agent orchestration with communication, heartbeats, waiting, step-by-step, and dataset suggestions while keeping execution ("compiling") primary.
