from agent.graph import build_graph
from bot.tg_bot import build_client, build_listener
from utils.config import load_config
from langgraph.checkpoint.sqlite import SqliteSaver
import telebot
import os



def main():
    config = load_config('../config.yaml')

    bot = telebot.TeleBot(config['app']['tg_bot_token'])

    for var, val in config.get('langsmith', {}).items():
        os.environ[var] = val


    with SqliteSaver.from_conn_string(config['app']['sqlite_path']) as memory:
        graph = build_graph(
            bot_client=build_client(bot),
            checkpointer=memory,
            llm_config=config['llm']
        )
        # from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
        # from PIL import Image
        # from io import BytesIO
        #
        # Image.open(BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))).save('../data/agent.png', 'PNG')

        listener = build_listener(
            bot=bot,
            graph=graph
        )
        listener.polling(none_stop=True)

if __name__ == "__main__":
    main()