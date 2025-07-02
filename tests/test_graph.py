import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.agent.graph import InputClassifierDecision, build_graph, AgentState, HISTORY_WINDOW

# Пример входного состояния
def get_basic_state() -> AgentState:
    return {
        "user_id": 1,
        "message_from_user": "Hello!",
        "decision": "free_answer",
        "chat_history": []
    }

@patch("src.agent.graph.ChatOpenAI")
def test_preprocess_adds_human_message(mock_llm_class):
    from src.agent.graph import build_graph

    mock_bot = MagicMock()
    mock_checkpoint = MagicMock()
    llm_config = {"temperature": 0.1}

    graph = build_graph(mock_bot, mock_checkpoint, llm_config)

    # Получаем функцию по имени
    preprocess_node = graph.nodes.get("preprocess")
    state = get_basic_state()
    result = preprocess_node.invoke(state)

    assert result["chat_history"][-1].content == "Hello!"
    assert result["message_from_user"] is None

@patch("src.agent.graph.ChatOpenAI")
def test_classify_input_sets_decision(mock_llm_class):
    from src.agent.graph import build_graph

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = InputClassifierDecision(action="free_answer")
    mock_llm.with_structured_output.return_value = mock_llm
    mock_llm_class.return_value = mock_llm

    mock_bot = MagicMock()
    mock_checkpoint = MagicMock()
    llm_config = {"temperature": 0.1}

    graph = build_graph(mock_bot, mock_checkpoint, llm_config)
    classify_node = graph.nodes.get("classify_input")

    state = get_basic_state()
    result = classify_node.invoke(state)

    assert result["decision"] == "free_answer"