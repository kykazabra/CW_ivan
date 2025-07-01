import telebot
from langgraph.graph import StateGraph
from time import sleep
import telegramify_markdown

user_waiting_answers = {}
tick_limit = 100
tick_time = 3

class TgBotClient:
    """Кастомный клиент для взаимодействия с API мессенджера"""

    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    def send_text_to_user(self, user: int, text: str) -> None:
        """Функция отправки сообщения определенному пользователю"""

        text = telegramify_markdown.markdownify(content=text)
        self.bot.send_message(chat_id=user, text=text, parse_mode='MarkdownV2')

    def acquire_info_from_user(self, user: int, text: str) -> str:
        """Функция дозапроса информации у определенного пользователя"""

        text = telegramify_markdown.markdownify(content=text)
        self.bot.send_message(chat_id=user, text=text, parse_mode='MarkdownV2')
        user_waiting_answers[user] = None

        for _ in range(tick_limit):
            sleep(tick_time)

            if user_waiting_answers[user]:
                return user_waiting_answers.pop(user)

        return 'Пользователь не дал ответа'

def build_client(bot: telebot.TeleBot) -> TgBotClient:
    """Функция сборки клиента мессенджера"""

    return TgBotClient(bot=bot)

def build_listener(bot: telebot.TeleBot, graph: StateGraph) -> telebot.TeleBot:
    """Функция сборки Lister бота для обработки входящих ивентов из мессенджера"""

    bot.set_my_short_description('Самый лучший бот - нутрициолог')

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Привет, я бот - нутрициолог!\n\nМожешь задавать мне любые вопросы по теме')

    @bot.message_handler(content_types='text')
    def message_reply(message):
        if message.chat.id in user_waiting_answers:
            user_waiting_answers[message.chat.id] = message.text
            return

        graph.invoke({
            'user_id': message.chat.id,
            'message_from_user': message.text
        }, config={"configurable": {"thread_id": message.chat.id}})

    return bot

