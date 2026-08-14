"""Chunking: one chunk per page. Same code as the notebook, as a function."""

from ragwire.loaders.page_loader import PageLoader
from ragwire.processing.splitter import PageSplitter

loader = PageLoader()
splitter = PageSplitter()


def split_pages(path):
    """Return one chunk per page of a document."""
    doc = loader.load(path)
    return splitter.split(doc["text_content"], pages=doc["pages"], file_type=doc["file_type"])
