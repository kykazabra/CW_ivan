import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch
from src.bot.tg_bot import TgBotClient, user_waiting_answers

def test_send_text_to_user():
    mock_bot = MagicMock()
    tg_client = TgBotClient(bot=mock_bot)

    tg_client.send_text_to_user(user=123, text="Hello **world**")

    mock_bot.send_message.assert_called_once_with(
        chat_id=123,
        text="Hello *world*\n",
        parse_mode='MarkdownV2'
    )

@patch("src.bot.tg_bot.sleep", return_value=None)  # ускорим тест
def test_acquire_info_from_user(mock_sleep):
    mock_bot = MagicMock()
    tg_client = TgBotClient(bot=mock_bot)

    result = tg_client.acquire_info_from_user(user=456, text="Enter info:")

    mock_bot.send_message.assert_called_once()