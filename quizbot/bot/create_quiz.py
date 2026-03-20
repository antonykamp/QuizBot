"""
Module with methods to create a quiz with a telegram bot
"""

import asyncio
import logging
import pickle
from argon2 import PasswordHasher
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ChatAction
from telegram.ext import ConversationHandler
from quizbot.quiz.question_factory import QuestionBool, QuestionChoice,\
    QuestionChoiceSingle, QuestionNumber, QuestionString
from quizbot.quiz.quiz import Quiz
from quizbot.bot.models import QuizModel

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Dict with string and associated question class
dict_question_types = {
    'Ask for a number': QuestionNumber,
    'Ask for a string': QuestionString,
    'Ask for a boolean value': QuestionBool,
    'Ask a multiple choice question': QuestionChoice,
    'Ask a multiple choice question with one correct answer': QuestionChoiceSingle
}


async def start(update, context):
    """
    Starts a conversation about quiz creation.
    Welcomes the user and asks for the type of the first question.
    """
    logger.info('[%s] Creation initialized', update.message.from_user.username)

    if context.user_data.get('quiz') is not None:
        # user is in the middle of a quiz and cant attempt to a second one
        logger.info('[%s] Creation canceled, because the user is in the middle of a creation.',
                    update.message.from_user.username)
        await update.message.reply_text(
            "You're in the middle of a creation 😉 "
            "You can't create a second one at the same time 😁\n"
            'If you want to cancel your creation, enter /cancelCreate.',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # Init Quiz for user
    context.user_data['quiz'] = Quiz(update.message.from_user.username)

    # Asks for type of first question
    list_question = [[el] for el in list(dict_question_types.keys())]
    await update.message.reply_text(
        "Hi 😃 Let's create a new quiz!\n"
        "What type of question should the first one be?\n"
        'If you want to cancel your creation, enter /cancelCreate.',
        reply_markup=ReplyKeyboardMarkup(
            list_question, one_time_keyboard=True)
    )

    return 'ENTER_TYPE'


async def cancel(update, context):
    """
    Cancels a creation ofa quiz by deleting the users' entries.
    """
    logger.info('[%s] Creation canceled by user',
                update.message.from_user.username)

    # Delete user data
    context.user_data.clear()
    await update.message.reply_text(
        "I canceled the creation process. See you next time. 🙋‍♂️",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def enter_type(update, context):
    """
    After entering the new question type, it asks for the question itself,
    if the entered string isn't 'Enter'.
    Otherwise, it asks if the question should be displayed in random order.
    """

    if update.message.text == "Enter":
        # User dont want to add more questions
        # Asks for randomness
        await update.message.reply_text(
            "Should the questions be displayed in random order? 🤔",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        logger.info('[%s] Completed question creation',
                    update.message.from_user.username)
        return 'ENTER_RANDOMNESS_QUIZ'

    # TODO What if type doesnt exisit
    # Save question type
    context.user_data['questtype'] = dict_question_types[update.message.text]

    await update.message.reply_text("What is the question? 🤔")
    return 'ENTER_QUESTION'


async def enter_question(update, context):
    """
    Asks for the correct answer to the question after entering the question itself.
    """

    # Save question in user_data
    context.user_data['question'] = update.message.text

    logger.info('[%s] Entered new question type "%s"',
                update.message.from_user.username, update.message.text)

    # Ask for correct answer in different ways
    if context.user_data['questtype'] == QuestionChoiceSingle:
        reply_text = "Please enter ONE correct answer ☝️"
    elif context.user_data['questtype'] == QuestionChoice:
        reply_text = "Please enter the correct answers separated by ', ' 🙆‍♂️"
    else:
        reply_text = "Please enter the correct answer 🙆‍♂️"

    await update.message.reply_text(reply_text)
    return 'ENTER_ANSWER'


async def enter_answer(update, context):
    """
    After entering the correct answer it tries to process it.
    If it fails, it asks for the correct answer again.
    Otherwise, it asks for additional possible answers,
    if the question is an instance of QuestionChoice.
    Otherwise, it adds the question to the quiz and asks for the type of the next question.
    """

    # Save correct answer in user_data
    context.user_data['answer'] = update.message.text

    # Try to init question instance
    QuestionType = context.user_data['questtype']
    try:
        context.user_data['questionInstance'] = QuestionType(context.user_data['question'],
                                                              context.user_data['answer'])
    except AssertionError:
        # TODO specify exceptions
        # Error because it isnt a number, no entry, not True/False,...
        await update.message.reply_text(
            "Sorry. Something went wrong by entering your answer. Please try again. 😕")
        logger.info('[%s] Entering correct answer "%s" failed',
                    update.message.from_user.username, update.message.text)
        return 'ENTER_ANSWER'

    logger.info('[%s] Entering correct answer "%s" accepted',
                update.message.from_user.username, update.message.text)

    if isinstance(context.user_data['questionInstance'], QuestionChoice):
        # If QuestionChoice instance, ask for additional possible answers
        await update.message.reply_text(
            "Please enter additional possible answers separated by ', ' 😁")
        return 'ENTER_POSSIBLE_ANSWER'

    # Add question to quiz
    context.user_data['quiz'].add_question(
        context.user_data['questionInstance'])

    # Asks for type of next question
    list_question = [[el] for el in list(dict_question_types.keys())]
    await update.message.reply_text(
        "What type of question should the next one be? "
        "If you don't have more questions, press 'Enter'.",
        reply_markup=ReplyKeyboardMarkup(
            list_question + [['Enter']], one_time_keyboard=True)
    )
    return 'ENTER_TYPE'


async def enter_possible_answer(update, context):
    """
    After entering additional possible answers, it asks whether the order of the answers
    should be random.
    """

    list_possible_answers = update.message.text.split(', ')
    # Add possible answers to question
    for answer in list_possible_answers:
        context.user_data['questionInstance'].add_possible_answer(answer)

    logger.info('[%s] Entered additional possible answers',
                update.message.from_user.username)

    # Ask for
    await update.message.reply_text(
        "Should the answers be displayed in random order? 🤔",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RANDOMNESS_QUESTION'


async def enter_randomness_question(update, context):
    """
    After entering whether the order if the answers should be random,
    it adds the question to the quiz.
    After that, it asks for the type of next question.
    """

    # Check for correct input
    if update.message.text not in ('Yes', 'No'):
        await update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the answers be displayed in random order?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RANDOMNESS_QUESTION'

    context.user_data['questionInstance'].is_random = update.message.text == 'Yes'
    logger.info('[%s] Entered randomness of the order of possible answers',
                update.message.from_user.username)

    # Add question to quiz
    context.user_data['quiz'].add_question(
        context.user_data['questionInstance'])
    logger.info('[%s] Added the question to the quiz',
                update.message.from_user.username)

    # Asks for type of next question
    list_question = [[el] for el in list(dict_question_types.keys())]
    await update.message.reply_text(
        "What type of question should the next one be? "
        "If you don't have more questions, press 'Enter'.",
        reply_markup=ReplyKeyboardMarkup(
            list_question + [['Enter']], one_time_keyboard=True)
    )
    return 'ENTER_TYPE'


async def enter_randomness_quiz(update, context):
    """
    After entering whether the order if the questions should be random,
    it asks if the result of the question be displayed after the question itself.
    """

    # Check for correct input
    if update.message.text not in ('Yes', 'No'):
        await update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the questions be displayed in random order?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RANDOMNESS_QUIZ'

    # Process input
    context.user_data['quiz'].is_random = update.message.text == 'Yes'

    # Ask for displaying result after question
    await update.message.reply_text(
        "Should the result of the question be displayed after the question?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RESULT_AFTER_QUESTION'


async def enter_result_after_question(update, context):
    """
    After entering whether the result of the question should be displayed after the question itself,
    it asks if the result of every question be displayed after the quiz.
    """

    # Check for correct input
    if update.message.text not in ('Yes', 'No'):
        await update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the result of the question be displayed after the question?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RESULT_AFTER_QUESTION'

    # Process input
    context.user_data['quiz'].show_results_after_question = update.message.text == 'Yes'

    # Ask for displaying result of every question after quiz
    await update.message.reply_text(
        "Should the result of every question be displayed after the quiz?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RESULT_AFTER_QUIZ'


async def enter_result_after_quiz(update, context):
    """
    After entering whether the result of every question should be displayed after the quiz,
    it asks for the name of the quiz?
    """

    # Check for correct input
    if update.message.text not in ('Yes', 'No'):
        await update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the result of every question be displayed after the quiz?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RESULT_AFTER_QUIZ'

    # Process input
    context.user_data['quiz'].show_results_after_quiz = update.message.text == 'Yes'

    # Ask for name of quiz
    await update.message.reply_text(
        "Great! 😃 I created a new quiz!\nHow should I name it? ✏️"
    )

    return 'ENTER_QUIZ_NAME'


async def enter_quiz_name(update, context):
    """
    After entering the name of the quiz, it looks up if the quiz name is occupied.
    If unique, asks whether the user wants to set a password.
    """

    logger.info('[%s] Completed quiz creation',
                update.message.from_user.username)
    quizname = update.message.text

    # Bot is typing during database query
    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)

    # Query for question with input name
    username = update.message.from_user.username
    Session = context.bot_data['Session']
    session = Session()
    try:
        result = await asyncio.to_thread(
            session.query(QuizModel).filter_by(username=username, quizname=quizname).first
        )
    finally:
        session.close()
    if result is not None:
        # Quiz with quizname already exists
        await update.message.reply_text(
            "Sorry. You already have a quiz named {} 😕\nPlease try something else".format(
                quizname)
        )
        logger.info('[%s] Quiz with name "%s" already exists',
                    update.message.from_user.username, update.message.text)

        return 'ENTER_QUIZ_NAME'

    # Store quizname for later save
    context.user_data['quizname'] = quizname

    # Ask if the user wants to set a password
    await update.message.reply_text(
        "Do you want to set a password for this quiz? 🔒\n"
        "Other users will need it to attempt the quiz. You can always attempt without it.",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )
    return 'ENTER_PASSWORD_CHOICE'


async def enter_password_choice(update, context):
    """
    After choosing whether to set a password, either asks for the password
    or saves the quiz without one.
    """
    if update.message.text == 'No':
        return await _save_quiz(update, context, password=None)

    if update.message.text == 'Yes':
        await update.message.reply_text("Please enter the password 🔑")
        return 'ENTER_PASSWORD'

    # Invalid input
    await update.message.reply_text(
        "Thats not a 'Yes' or a 'No' 😕"
        "Do you want to set a password for this quiz?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )
    return 'ENTER_PASSWORD_CHOICE'


async def enter_password(update, context):
    """
    Hashes the password and saves the quiz to the database.
    """
    ph = PasswordHasher()
    hashed = ph.hash(update.message.text)
    return await _save_quiz(update, context, password=hashed)


async def _save_quiz(update, context, password=None):
    """
    Saves the quiz to the database with an optional password hash.
    """
    username = update.message.from_user.username
    quizname = context.user_data['quizname']

    Session = context.bot_data['Session']
    session = Session()
    try:
        quiz_row = QuizModel(
            username=username,
            quizname=quizname,
            quizinstance=pickle.dumps(context.user_data['quiz']),
            password=password,
        )
        session.add(quiz_row)
        await asyncio.to_thread(session.commit)
    finally:
        session.close()
    await update.message.reply_text(
        "Great! 🥳 I saved your new quiz."
        "You can attempt to it by the name {}.".format(quizname),
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info('[%s] Quiz saved as "%s"',
                update.message.from_user.username, quizname)
    # Delete user data
    context.user_data.clear()
    return ConversationHandler.END
