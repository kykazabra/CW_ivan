import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.tools import rag_tool, search_tool
from langchain_core.tools import Tool
from langchain_tavily import TavilySearch
from unittest.mock import patch


def test_rag_tool_structure():
    assert isinstance(rag_tool, Tool)
    assert rag_tool.name == "retrieve_nutrition_hints"
    assert "нутрциологии" in rag_tool.description


def test_search_tool_init():
    assert isinstance(search_tool, TavilySearch)
    assert search_tool.max_results == 3
    assert search_tool.topic == "general"
    assert hasattr(search_tool, "api_wrapper")