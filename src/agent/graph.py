from humanfriendly.terminal import message
from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Union, Annotated, List

from sympy import content
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .prompts import (INPUT_CLASSIFYING_PROMPT,
                      GET_MORE_INFO_PROMPT,
                      RAG_AGENT_PROMPT,
                      SEARCH_AGENT_PROMPT,
                      CLASSIFYING_DECISIONS_DESCRIPTION,
                      BASE_SYSTEM_PROMPT)
from .tools import rag_tool, search_tool
from src.bot.tg_bot import TgBotClient
# TODO: ридми, докерфайл, тесты

HISTORY_WINDOW = 10


class InputClassifierDecision(BaseModel):
    """Решение, какое действие выполнить следующим"""

    action: Literal['free_answer', 'knowledge_base', 'web_search', 'acquire_info'] = Field(description=CLASSIFYING_DECISIONS_DESCRIPTION)


class AgentState(TypedDict):
    """State агента"""

    user_id: int
    message_from_user: str
    decision: Literal['free_answer', 'knowledge_base', 'web_search', 'acquire_info']
    chat_history: List[Union[HumanMessage, AIMessage, SystemMessage]]


def build_graph(bot_client: TgBotClient, checkpointer: BaseCheckpointSaver, llm_config: Dict) -> StateGraph:
    """Функция сборки графа Langgraph"""

    llm = ChatOpenAI(**llm_config)

    graph = StateGraph(AgentState)

    def preprocess(state: AgentState) -> AgentState:
        """Node предобработки входящего State"""

        if BASE_SYSTEM_PROMPT:
            base = [SystemMessage(content=BASE_SYSTEM_PROMPT)]
        else:
            base = []

        if not state.get("chat_history"):
            state["chat_history"] = base

        if state.get("message_from_user"):
            state["chat_history"].append(HumanMessage(content=state["message_from_user"]))
            state["message_from_user"] = None

        if len(state["chat_history"]) > HISTORY_WINDOW:
            state["chat_history"] = base + state["chat_history"][-HISTORY_WINDOW:]

        return state

    def classify_input(state: AgentState) -> AgentState:
        """Node принятия решения о дальнейшем действии"""

        classifying_llm = llm.with_structured_output(InputClassifierDecision)

        state["decision"] = classifying_llm.invoke(state["chat_history"] + [SystemMessage(content=INPUT_CLASSIFYING_PROMPT)]).action

        return state

    def free_answer(state: AgentState) -> AgentState:
        """Node свободного ответа с помощью LLM"""

        state["chat_history"].append(llm.invoke(state["chat_history"]))

        return state

    def knowledge_base(state: AgentState) -> AgentState:
        """Node обращения к RAG агенту по базе знаний"""

        rag_agent = create_react_agent(
            model=llm,
            tools=[rag_tool],
            name='RAG_Agent'
        )

        messages = state["chat_history"] if not RAG_AGENT_PROMPT else state["chat_history"] + [SystemMessage(content=RAG_AGENT_PROMPT)]

        state["chat_history"].append(rag_agent.invoke({"messages": messages})['messages'][-1])

        return state

    def acquire_info(state: AgentState) -> AgentState:
        """Node HITL"""

        state["chat_history"].append(llm.invoke(state["chat_history"] + [SystemMessage(content=GET_MORE_INFO_PROMPT)]))

        state["chat_history"].append(HumanMessage(content=bot_client.acquire_info_from_user(
            user=state["user_id"],
            text=state["chat_history"][-1].content
        )))

        return state

    def web_search(state: AgentState) -> AgentState:
        """Node обращения к Web Search агенту"""

        search_agent = create_react_agent(
            model=llm,
            tools=[search_tool],
            name='Web_Search_Agent'
        )

        messages = state["chat_history"] if not SEARCH_AGENT_PROMPT else state["chat_history"] + [SystemMessage(content=SEARCH_AGENT_PROMPT)]


        state["chat_history"].append(search_agent.invoke({"messages": messages})['messages'][-1])

        return state

    def send_to_user(state: AgentState) -> AgentState:
        """Node отправки результата обратно к пользователю через кастомный клиент"""

        bot_client.send_text_to_user(
            user=state["user_id"],
            text=state["chat_history"][-1].content
        )

        return state

    graph.add_node("preprocess", preprocess)
    graph.add_node("classify_input", classify_input)
    graph.add_node("free_answer", free_answer)
    graph.add_node("knowledge_base", knowledge_base)
    graph.add_node("acquire_info", acquire_info)
    graph.add_node("web_search", web_search)
    graph.add_node("send_to_user", send_to_user)

    graph.set_entry_point("preprocess")

    graph.add_conditional_edges(
        "classify_input",
        lambda state: state["decision"],
        {
            "free_answer": "free_answer",
            "knowledge_base": "knowledge_base",
            "acquire_info": "acquire_info",
            "web_search": "web_search"
        }
    )

    graph.add_edge("preprocess", "classify_input")
    graph.add_edge("acquire_info", "preprocess")
    graph.add_edge("free_answer", "send_to_user")
    graph.add_edge("knowledge_base", "send_to_user")
    graph.add_edge("web_search", "send_to_user")
    graph.add_edge("send_to_user", END)

    return graph.compile(checkpointer=checkpointer)