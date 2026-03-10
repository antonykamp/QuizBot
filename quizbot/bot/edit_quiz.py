"""
Module with methods to rename and remove a quiz with a telegram bot
"""
import asyncio
import logging
from telegram.constants import ChatAction
from telegram.ext import ConversationHandler
from quizbot.bot.models import QuizModel

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_remove(update, _):
    """Start a process to remove a quiz."""

    logger.info('[%s] Removing process initialized',
                update.message.from_user.username)
    await update.message.reply_text(
        "Which quiz do you want to delete? 🙂"
    )
    return 'ENTER_NAME'


async def enter_name_remove(update, context):
    """Deltes a quiz after entering its' name."""

    quiz_creator = update.message.from_user.username
    quiz_name = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    Session = context.bot_data['Session']
    session = Session()
    try:
        # Checks if the quiz exists
        result = await asyncio.to_thread(
            session.query(QuizModel).filter_by(username=quiz_creator, quizname=quiz_name).first
        )
        if result is None:
            logger.info('[%s] Entered quiz %s doesn\'t exist',
                        update.message.from_user.username, quiz_name)
            await update.message.reply_text(
                "The quiz '{}' doesn't exist 😕\nPlease try again or cancel process with /cancelEdit 🙆‍♂️".format(
                    quiz_name)
            )
            return 'ENTER_NAME'

        # Deletes the quiz
        await asyncio.to_thread(session.delete, result)
        await asyncio.to_thread(session.commit)
    finally:
        session.close()
    logger.info('[%s] Removed %s',
                update.message.from_user.username, quiz_name)
    await update.message.reply_text(
        "I deleted '{}' 👍".format(quiz_name)
    )
    return ConversationHandler.END


async def start_rename(update, _):
    """Starts a process to rename a quiz."""

    logger.info('[%s] Renaming process initialized',
                update.message.from_user.username)
    await update.message.reply_text(
        "Which quiz do you want to rename? ✏️"
    )
    return 'ENTER_OLD_NAME'


async def enter_old_name(update, context):
    """After entering the old quiz name, it asks for the new one."""

    quiz_creator = update.message.from_user.username
    old_quiz_name = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    Session = context.bot_data['Session']
    session = Session()
    try:
        result = await asyncio.to_thread(
            session.query(QuizModel).filter_by(username=quiz_creator, quizname=old_quiz_name).first
        )
    finally:
        session.close()
    if result is None:

        logger.info("[%s] Entered old quiz '%s' doesn\'t exist",
                    update.message.from_user.username, old_quiz_name)
        await update.message.reply_text(
            "The quiz '{}' doesn't exist 😕\nPlease try again or cancel process with /cancelEdit 🙆‍♂️".format(
                old_quiz_name)
        )
        return 'ENTER_OLD_NAME'

    logger.info("[%s] Entered old quiz name '%s'",
                update.message.from_user.username, old_quiz_name)
    # Saves the old quiz name in user_data
    context.user_data['old_quiz_name'] = old_quiz_name
    await update.message.reply_text(
        "How should I name it? 🤔"
    )
    return 'ENTER_NEW_NAME'


async def enter_new_name(update, context):
    """After entering the new name of the quiz, it renames it."""

    quiz_creator = update.message.from_user.username
    new_quiz_name = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    Session = context.bot_data['Session']
    session = Session()
    try:
        # Check if a quiz with the name already exists
        result = await asyncio.to_thread(
            session.query(QuizModel).filter_by(username=quiz_creator, quizname=new_quiz_name).first
        )
        if result is not None:

            logger.info("[%s] Entered new quiz '%s' already exists",
                        update.message.from_user.username, new_quiz_name)
            await update.message.reply_text(
                "The quiz '{}' already exists 😕\nPlease try again or cancel process with /cancelEdit 🙆‍♂️".format(
                    new_quiz_name)
            )
            return 'ENTER_NEW_NAME'

        # Get old quizname and update database
        old_quiz_name = context.user_data['old_quiz_name']
        old_quiz = await asyncio.to_thread(
            session.query(QuizModel).filter_by(username=quiz_creator, quizname=old_quiz_name).first
        )
        if old_quiz is None:
            logger.info("[%s] Quiz '%s' was deleted before renaming",
                        update.message.from_user.username, old_quiz_name)
            await update.message.reply_text(
                "The quiz '{}' doesn't exist anymore 😕".format(old_quiz_name)
            )
            return ConversationHandler.END
        old_quiz.quizname = new_quiz_name
        await asyncio.to_thread(session.commit)
    finally:
        session.close()
    await update.message.reply_text(
        "I renamed '{}' to '{}' 🥳".format(old_quiz_name, new_quiz_name)
    )
    logger.info("[%s] Updated quiz '%s' to '%s'",
                update.message.from_user.username, new_quiz_name, old_quiz_name)

    # delete user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_edit(update, context):
    """Cancels the process of deletion or renaming."""
    await update.message.reply_text(
        "I canceled the editing process."
    )
    logger.info("[%s] Canceled editing process by user",
                update.message.from_user.username)

    # delete user data
    context.user_data.clear()
    return ConversationHandler.END
