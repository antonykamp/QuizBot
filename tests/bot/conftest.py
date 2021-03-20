"""
Basic example for a bot that uses inline keyboards.
"""
from telegram.ext import Updater
import os

update = Updater(os.environ.get("UPDATER_ID"), use_context=True)


def pytest_runtest_setup():
    """Initializes the test bot"""

    # setup handlers
    from quizbot.bot.bot import setup_bot
    setup_bot(update)

    # Start the Bot
    update.start_polling()


def pytest_runtest_teardown():
    """Shuts down the test bot"""
    update.stop()
