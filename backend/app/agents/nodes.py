import json
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL, MAX_RETRIES
from app.agents.state import AgentState
from app.agents.tools import analyze_dataframe_schema, check_code_result
from app.services.data_loader import get_dataset_info
from app.services.sandbox import SandboxService

# Initialize the LLM
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0.2,
)

# Bind tools
llm_with_tools = llm.bind_tools([analyze_dataframe_schema, check_code_result])


SYSTEM_PROMPT = """You are an expert data analysis AI assistant. You help users analyze datasets by writing and executing Python code.

Your capabilities:
1. Analyze dataset schemas to understand the data
2. Create comprehensive analysis plans
3. Write clean, efficient Python code for data analysis
4. Generate visualizations using matplotlib, seaborn, or plotly
5. Fix errors in generated code by reading error messages

Analysis Guidelines:
- Always start by understanding the data structure
- Use pandas for data manipulation
- Create clear, informative visualizations with proper labels, titles, and legends
- Handle missing data appropriately
- Provide statistical summaries when relevant
- Explain your findings in plain language
- Use seaborn's darkgrid style for matplotlib plots
- Save matplotlib/seaborn plots as 'plot.png' to make them visible
- For plotly, create interactive figures

When writing code:
- Import all necessary libraries
- Use the variable 'df' for the dataset
- Handle edge cases (empty data, missing values)
- Print key findings alongside visualizations
- Keep code well-commented"""


def _get_schema_text(state: AgentState) -> str:
    """Extract schema text from dataset info."""
    info = state.get("dataset_info", {})
    if not info:
        return json.dumps({"error": "No dataset info available"})
    return json.dumps({
        "columns": info.get("columns", []),
        "dtypes": info.get("dtypes", {}),
        "row_count": info.get("row_count", 0),
        "preview": info.get("preview", []),
        "numeric_stats": info.get("numeric_stats", {}),
    }, default=str)


async def analyze_schema_node(state: AgentState) -> dict:
    """Analyze the dataset schema and provide a summary."""
    schema_text = _get_schema_text(state)
    result = analyze_dataframe_schema.invoke({"dataset_info": schema_text})

    analysis_msg = AIMessage(
        content=f"I've analyzed the dataset schema:\n\n{result}\n\nLet me now plan the analysis."
    )

    return {
        "messages": [analysis_msg],
        "analysis_plan": "",
    }


async def plan_analysis_node(state: AgentState) -> dict:
    """Plan the analysis approach based on the user's question and schema."""
    question = state.get("user_question", "")
    schema_text = _get_schema_text(state)

    plan_prompt = f"""Given this dataset schema:
{schema_text}

And the user's question: "{question}"

Create a detailed step-by-step analysis plan. Include:
1. What data transformations are needed
2. What statistical analyses to perform
3. What visualizations to create
4. What conclusions to draw

Keep the plan focused and actionable."""

    response = await llm.ainvoke([HumanMessage(content=plan_prompt)])
    plan = response.content

    return {
        "messages": [AIMessage(content=f"**Analysis Plan:**\n\n{plan}")],
        "analysis_plan": plan,
    }


async def generate_code_node(state: AgentState) -> dict:
    """Generate Python code based on the analysis plan."""
    plan = state.get("analysis_plan", "")
    question = state.get("user_question", "")
    schema_text = _get_schema_text(state)

    code_prompt = f"""Dataset schema:
{schema_text}

Analysis plan: {plan}

User question: {question}

Write Python code to perform this analysis on the dataset. The data is loaded in a pandas DataFrame called 'df'.

Requirements:
1. Import pandas, numpy, matplotlib.pyplot, seaborn, and plotly.express
2. Set seaborn style: sns.set_style("darkgrid")
3. Handle missing data appropriately
4. Create clear visualizations with titles, labels, and legends
5. Save matplotlib/seaborn plots as 'plot.png' (this is critical for displaying them)
6. Print key findings and insights
7. If using plotly, save the figure as an HTML string and print it
8. Keep the code efficient and well-commented

Return ONLY the Python code, no explanation."""

    response = await llm.ainvoke([HumanMessage(content=code_prompt)])
    code = response.content.strip()

    # Clean code blocks if present
    if code.startswith("```python"):
        code = code[len("```python"):]
    if code.startswith("```"):
        code = code[len("```"):]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    return {
        "messages": [AIMessage(content=f"```python\n{code}\n```")],
        "generated_code": code,
    }


async def execute_code_node(state: AgentState) -> dict:
    """Execute the generated code in the E2B sandbox."""
    code = state.get("generated_code", "")
    file_path = state.get("dataset_file_path", "")

    if not code:
        return {"execution_result": {"error": {"value": "No code to execute"}}}

    # Prepend data loading code
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".json":
        loader = "import pandas as pd\ndf = pd.read_json(r'{path}')\n"
    else:
        loader = "import pandas as pd\ndf = pd.read_csv(r'{path}')\n"

    full_code = loader.format(path=file_path) + code

    try:
        async with SandboxService() as sandbox:
            await sandbox.start()
            result = await sandbox.run_code(full_code)
    except Exception as e:
        result = {"error": {"name": "SandboxError", "value": str(e), "traceback": ""}}

    return {"execution_result": result}


async def fix_error_node(state: AgentState) -> dict:
    """Fix errors in the generated code."""
    code = state.get("generated_code", "")
    error = state.get("execution_result", {}).get("error", {})
    error_count = state.get("error_count", 0) + 1
    question = state.get("user_question", "")

    fix_prompt = f"""The following code produced an error:

```python
{code}
```

Error:
{error.get('name', 'Unknown')}: {error.get('value', '')}
Traceback:
{error.get('traceback', '')}

Original question: {question}

Please fix the code to resolve this error. Return ONLY the corrected Python code."""

    response = await llm.ainvoke([HumanMessage(content=fix_prompt)])
    fixed_code = response.content.strip()

    # Clean code blocks
    if fixed_code.startswith("```python"):
        fixed_code = fixed_code[len("```python"):]
    if fixed_code.startswith("```"):
        fixed_code = fixed_code[len("```"):]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code[:-3]
    fixed_code = fixed_code.strip()

    return {
        "generated_code": fixed_code,
        "error_count": error_count,
        "messages": [AIMessage(content=f"Fixed code (attempt {error_count}):\n```python\n{fixed_code}\n```")],
    }


async def synthesize_node(state: AgentState) -> dict:
    """Synthesize the final response with results and visualizations."""
    execution_result = state.get("execution_result", {})
    question = state.get("user_question", "")
    plots = execution_result.get("plots", [])
    plotly_figures = execution_result.get("plotly_figures", [])
    stdout = "\n".join(execution_result.get("stdout", []))
    stderr = "\n".join(execution_result.get("stderr", []))
    error = execution_result.get("error")

    if error:
        # Summarize error
        summary_prompt = f"""The analysis of "{question}" encountered an error after {MAX_RETRIES} retries.

Error: {error.get('value', '')}

Please explain what went wrong and suggest how the user could modify their question or data to get better results."""
        response = await llm.ainvoke([HumanMessage(content=summary_prompt)])
        return {
            "final_response": response.content,
            "plots": plots,
            "plotly_figures": plotly_figures,
        }

    # Synthesize findings
    synthesis_prompt = f"""The data analysis code ran successfully for the question: "{question}"

Output:
{stdout[:2000]}

{'Stderr warnings:' + stderr[:1000] if stderr else ''}

Please provide a clear, concise summary of the findings. Include:
1. Key insights from the analysis
2. Important numbers or trends
3. What the visualizations show
4. Any limitations or caveats

Be conversational and helpful."""

    response = await llm.ainvoke([HumanMessage(content=synthesis_prompt)])

    return {
        "final_response": response.content,
        "plots": plots,
        "plotly_figures": plotly_figures,
    }
