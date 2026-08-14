"""Stream an agent's progress. The notebook and the Chainlit app both use this."""

from langchain_core.messages import HumanMessage


def stream_agent(agent, query, config, verbose=True):
    """Run one query and yield the agent's progress as it happens.

    Always yields ("answer", text) when the agent answers. By default it
    also yields each step of the loop as the agent works:
      ("tool_call", tool_name, args)      the agent decided to call a tool
      ("tool_result", tool_name, content) what the tool sent back, truncated
    Pass verbose=False to get the answer alone.

    The caller decides how to render the events, so the notebook can print
    them and the Chainlit app can draw them as steps in the UI.
    """
    for event in agent.stream({"messages": [HumanMessage(query)]},
                              config=config, stream_mode="updates"):
        for update in event.values():
            for message in update.get("messages", []):
                if message.type == "ai" and message.tool_calls:
                    if verbose:
                        for call in message.tool_calls:
                            yield "tool_call", call["name"], call["args"]
                elif message.type == "tool":
                    if verbose:
                        yield "tool_result", message.name, message.content[:200]
                elif message.type == "ai" and message.content:
                    yield "answer", message.content
