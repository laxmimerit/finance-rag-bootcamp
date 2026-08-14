"""Text extraction: PDF to markdown. Same code as the notebook, as a function."""

from ragwire.loaders.markitdown_loader import MarkItDownLoader

loader = MarkItDownLoader()


def pdf_to_markdown(path):
    """Return the markdown text of one PDF."""
    doc = loader.load(path)
    return doc["text_content"]
