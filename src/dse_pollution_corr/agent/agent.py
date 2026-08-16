"""LangChain ReAct agent wired to OpenRouter."""

from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from dse_pollution_corr.agent.tools import AGENT_TOOLS, get_last_query_result

SYSTEM_PROMPT = """You are an analyst for the HKDSE exam results and Hong Kong air quality dataset.

Answer investigative questions by querying the DuckDB database. Use views when possible:
- v_exam_day_environment for exam dates joined to AQHI and wind
- v_category_a_performance for grade trends
- v_subject_year_aqhi for subject-year pollution summaries

Rules:
- Only use the provided SQL tools; do not invent numbers.
- Filter is_summary = false for subject-level results unless totals are requested.
- candidate_type is day_school or all.
- Category C grading changed in 2025; note scheme differences.
- pct_* columns are percentages 0-100.
- Prefer concise markdown answers with key numbers and filters used."""


def _build_llm() -> ChatOpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return ChatOpenAI(
        model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0,
        default_headers={
            "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "http://localhost:5173"),
            "X-Title": os.environ.get("OPENROUTER_APP_NAME", "dse-pollution-corr"),
        },
    )


def build_agent():
    llm = _build_llm()
    return create_agent(
        llm,
        AGENT_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        debug=os.environ.get("AGENT_VERBOSE", "").lower() in {"1", "true", "yes"},
    )


def run_agent(question: str) -> dict[str, Any]:
    agent = build_agent()
    max_iterations = int(os.environ.get("AGENT_MAX_ITERATIONS", "8"))
    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"recursion_limit": max_iterations * 2 + 1},
    )
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else ""

    query_result = get_last_query_result()
    sql = None
    chart = None
    preview = None
    if query_result:
        sql = query_result.get("sql")
        chart = query_result.get("chart")
        preview = {
            "columns": query_result.get("columns", []),
            "rows": query_result.get("rows", [])[:20],
            "row_count": query_result.get("row_count", 0),
        }

    return {
        "answer": answer,
        "sql": sql,
        "chart": chart,
        "preview": preview,
    }
