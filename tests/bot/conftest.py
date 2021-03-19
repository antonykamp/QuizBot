"""
Basic example for a bot that uses inline keyboards.
"""
from telegram.ext import Updater
from quizbot.bot.bot import setup_bot
import json

API_ID = 0
API_HASH = ""
SESSION_STR = ""
UPDATER_ID = ""
updater = None


def pytest_runtest_setup():
    """Initializes the test bot"""
    with open("../../TOKEN.json", "r") as read_file:
        data = json.load(read_file)
    API_ID = int(data['API_ID'])
    API_HASH = data['API_HASH']
    SESSION_STR = data['SESSION_STR']
    UPDATER_ID = data['UPDATER_ID']

    updater = Updater(UPDATER_ID, use_context=True)
    # setup handlers
    setup_bot(updater)

    # Start the Bot
    updater.start_polling()


def pytest_runtest_teardown():
    """Shuts down the test bot"""
    updater.stop()
