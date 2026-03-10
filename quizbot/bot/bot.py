"""
Telegram bot to create and attempt to quizzes.
"""

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters
import quizbot.bot.create_quiz as createQuiz
import quizbot.bot.attempt_quiz as attemptQuiz
import quizbot.bot.edit_quiz as editQuiz
from quizbot.bot.config import get_config, get_session_factory


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


async def print_help(update, _):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Hey! 🙋‍♂️ How can I help you?\n'
    )
    await update.message.reply_text(
        'What QuizBot is? 😃\n\n'
        'With QuizBot you can create quizzes with different question types. 🧐 You can\n'
        '- ask for a number,\n'
        '- ask for a string,\n'
        '- ask für a boolean value,\n'
        '- create multiple choice questions or\n'
        '- create multiple choice questions with one correct answer.\n'
        'If you want to create a new quiz, call /create. 🤓\n'
        'If you want to attempt a quiz, call /attempt. 🤔\n'
        'If you want to rename one of your quizzes, call /rename. ✏️\n'
        'If you want to delete one of your quizzes, call /remove.\n\n'
        'Have fun! 🥳'
    )


async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def setup_bot(app):
    """Setups the handlers"""

    # Conversation if the user wants to create a quiz
    create_states = {
        'ENTER_TYPE': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_type)],
        'ENTER_QUESTION': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_question)],
        'ENTER_ANSWER': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_answer)],
        'ENTER_POSSIBLE_ANSWER': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_possible_answer)],
        'ENTER_RANDOMNESS_QUESTION': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_randomness_question)],
        'ENTER_RANDOMNESS_QUIZ': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_randomness_quiz)],
        'ENTER_RESULT_AFTER_QUESTION': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_result_after_question)],
        'ENTER_RESULT_AFTER_QUIZ': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_result_after_quiz)],
        'ENTER_QUIZ_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, createQuiz.enter_quiz_name)],
    }
    create_handler = ConversationHandler(
        entry_points=[CommandHandler('create', createQuiz.start)],
        states=create_states,
        fallbacks=[CommandHandler('cancelCreate', createQuiz.cancel)]
    )
    app.add_handler(create_handler)

    # Conversation if the user wants to attempt a quiz
    attempt_states = {
        'ENTER_QUIZ': [MessageHandler(filters.TEXT & ~filters.COMMAND, attemptQuiz.enter_quiz)],
        'ENTER_ANSWER': [MessageHandler(filters.TEXT & ~filters.COMMAND, attemptQuiz.enter_answer)]
    }
    attempt_handler = ConversationHandler(
        entry_points=[CommandHandler('attempt', attemptQuiz.start)],
        states=attempt_states,
        fallbacks=[CommandHandler('cancelAttempt', attemptQuiz.cancel)]
    )
    app.add_handler(attempt_handler)

    # Conversation about remove or renaming exisiting quiz
    edit_states = {
        'ENTER_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, editQuiz.enter_name_remove)],
        'ENTER_OLD_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, editQuiz.enter_old_name)],
        'ENTER_NEW_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, editQuiz.enter_new_name)]
    }
    edit_handler = ConversationHandler(
        entry_points=[CommandHandler('rename', editQuiz.start_rename), CommandHandler(
            'remove', editQuiz.start_remove)],
        states=edit_states,
        fallbacks=[CommandHandler('cancelEdit', editQuiz.cancel_edit)]
    )
    app.add_handler(edit_handler)

    # help command
    app.add_handler(CommandHandler("help", print_help))

    # log all errors
    app.add_error_handler(error)


if __name__ == '__main__':
    config = get_config()
    Session = get_session_factory(config['DATABASE_URL'])

    app = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    app.bot_data['Session'] = Session

    setup_bot(app)

    if config['WEBHOOK']:
        app.run_webhook(
            listen="0.0.0.0",
            port=config['PORT'],
            url_path=config['TELEGRAM_TOKEN'],
            webhook_url=config['WEBHOOK'] + config['TELEGRAM_TOKEN'],
        )
    else:
        logger.info('No WEBHOOK set, starting in polling mode')
        app.run_polling()
