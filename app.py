"""Chainlit UI over the same agent the notebook built.

The tools come from scripts/tools.py and the streaming loop from
scripts/agent.py, so the notebook and this UI share one implementation.
Each chat session is its own memory thread, stored in SQLite, and tool
calls render as steps while the agent works.

    uv run chainlit run app.py
"""

import sqlite3
from pathlib import Path

import chainlit as cl
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver

from scripts.agent import stream_agent
from scripts.tools import get_filter_context, search_documents

model = ChatOllama(model="qwen3.8:27B", base_url="http://localhost:11434")

Path("db").mkdir(exist_ok=True)
conn = sqlite3.connect("db/chainlit_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

agent = create_agent(
    model=model,
    tools=[get_filter_context, search_documents],
    system_prompt=(
        "You are a helpful financial document assistant. "
        "For complex questions, break them down into simple sub-questions and answer each one before forming a final answer. "
        "Always use search_documents to retrieve information before answering. "
        "Never answer from general knowledge. "
        "Use get_filter_context before search_documents when the query involves specific metadata (company, year, document type, etc.). "
        "When a question asks about the whole collection, or for the highest, lowest, or a comparison across companies, first call get_filter_context to see which companies the collection holds, then search every relevant company before answering. "
        "If no relevant documents are found, say so. Do not guess or fabricate an answer. "
        "Always cite the source document in your answer."
    ),
    checkpointer=checkpointer,
)


@cl.on_message
async def answer(message: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    events = stream_agent(agent, message.content, config)
    next_event = cl.make_async(lambda: next(events, None))

    pending_args = {}
    while True:
        event = await next_event()
        if event is None:
            break
        if event[0] == "tool_call":
            pending_args[event[1]] = event[2]
        elif event[0] == "tool_result":
            async with cl.Step(name=event[1], type="tool") as step:
                step.input = str(pending_args.pop(event[1], ""))
                step.output = event[2]
        else:
            await cl.Message(content=event[1]).send()
