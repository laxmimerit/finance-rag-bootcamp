"""The agent's tools, explained in the notebook, ready for the Chainlit app.

The pipeline has auto_filter off, so filtering is the agent's job:
get_filter_context reports the metadata fields and the values the collection
actually stores, and the agent decides what filters to pass search_documents.
"""

from typing import Optional

from langchain.tools import tool

from scripts.pipeline import get_rag

rag = get_rag()


@tool
def get_filter_context(query: str) -> str:
    """Get available metadata fields, stored values, and filter suggestions for a query.

    Call this before search_documents when the query involves specific metadata
    (company, year, document type, etc.). Use the returned context to decide
    what filters to pass to search_documents.
    """
    return rag.get_filter_context(query)


@tool
def search_documents(query: str, filters: Optional[dict] = None) -> str:
    """Search the document knowledge base for relevant information.

    Args:
        query: The search query
        filters: Optional metadata filters decided from get_filter_context.
                 Pass {} or omit to search without filtering.
    """
    results = rag.retrieve(query, top_k=5, filters=filters)
    if not results:
        return "No relevant documents found."

    chunks = []
    for doc in results:
        source = doc.metadata.get("file_name", "unknown")
        page = doc.metadata.get("page_number")
        if page is not None:
            source = source + ", page " + str(page)
        chunks.append("[" + source + "]\n" + doc.page_content)

    return "\n\n---\n\n".join(chunks)
