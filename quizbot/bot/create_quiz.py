"""
Module with methods to create a quiz with a telegram bot
"""

import logging
import pickle
import pymongo
import os
from telegram import ReplyKeyboardMarkup, ChatAction
from telegram.ext import ConversationHandler
from telegram.replykeyboardremove import ReplyKeyboardRemove
from quizbot.quiz.question_factory import QuestionBool, QuestionChoice,\
    QuestionChoiceSingle, QuestionNumber, QuestionString
from quizbot.quiz.quiz import Quiz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

db = pymongo.MongoClient(os.environ.get('MONGODB')).quizzes

# Dict with user data like a quiz instance
userDict = dict()

# Dict with string and associated question class
dict_question_types = {
    'Ask for a number': QuestionNumber,
    'Ask for a string': QuestionString,
    'Ask for a boolean value': QuestionBool,
    'Ask a multiple choice question': QuestionChoice,
    'Ask a multiple choice question with one correct answer': QuestionChoiceSingle
}


def start(update, _):
    """
    Starts a conversation about quiz creation.
    Welcomes the user and asks for the type of the first question.
    """
    logger.info('[%s] Creation initialized', update.message.from_user.username)

    if update.message.from_user.id in userDict:
        # user is in the middle of a quiz and cant attempt to a second one
        logger.info('[%s] Creation canceled, because the user is in the middle of a creation.',
                    update.message.from_user.username)
        update.message.reply_text(
            "You're in the middle of a creation 😉 "
            "You can't create a second one at the same time 😁\n"
            'If you want to cancel your creation, enter /cancelCreate.',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # Init Quiz for user
    userDict[update.message.from_user.id] = {
        'quiz': Quiz(update.message.from_user.username)}

    # Asks for type of first question
    list_question = [[el] for el in list(dict_question_types.keys())]
    update.message.reply_text(
        "Hi 😃 Let's create a new quiz!\n"
        "What type of question should the first one be?\n"
        'If you want to cancel your creation, enter /cancelCreate.',
        reply_markup=ReplyKeyboardMarkup(
            list_question, one_time_keyboard=True)
    )

    return 'ENTER_TYPE'


def cancel(update, _):
    """
    Cancels a creation ofa quiz by deleting the users' entries.
    """
    logger.info('[%s] Creation canceled by user',
                update.message.from_user.username)

    # Delete user data
    userDict.pop(update.message.from_user.id)
    update.message.reply_text(
        "I canceled the creation process. See you next time. 🙋‍♂️",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def enter_type(update, _):
    """
    After entering the new question type, it asks for the question itself,
    if the entered string isn't 'Enter'.
    Otherwise, it asks if the question should be displayed in random order.
    """

    if update.message.text == "Enter":
        # User dont want to add more questions
        # Asks for randomness
        update.message.reply_text(
            "Should the questions be displayed in random order? 🤔",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        logger.info('[%s] Completed question creation',
                    update.message.from_user.username)
        return 'ENTER_RANDOMNESS_QUIZ'

    # TODO What if type doesnt exisit
    # Save question type
    user_id = update.message.from_user.id
    userDict[user_id]['questtype'] = dict_question_types[update.message.text]

    update.message.reply_text("What is the question? 🤔")
    return 'ENTER_QUESTION'


def enter_question(update, _):
    """
    Asks for the correct answer to the question after entering the question itself.
    """

    # Save question in userdict
    user_id = update.message.from_user.id
    userDict[user_id]['question'] = update.message.text

    logger.info('[%s] Entered new question type "%s"',
                update.message.from_user.username, update.message.text)

    # Ask for correct answer in different ways
    if userDict[user_id]['questtype'] == QuestionChoiceSingle:
        reply_text = "Please enter ONE correct answer ☝️"
    elif userDict[user_id]['questtype'] == QuestionChoice:
        reply_text = "Please enter the correct answers separated by ', ' 🙆‍♂️"
    else:
        reply_text = "Please enter the correct answer 🙆‍♂️"

    update.message.reply_text(reply_text)
    return 'ENTER_ANSWER'


def enter_answer(update, _):
    """
    After entering the correct answer it tries to process it.
    If it fails, it asks for the correct answer again.
    Otherwise, it asks for additional possible answers,
    if the question is an instance of QuestionChoice.
    Otherwise, it adds the question to the quiz and asks for the type of the next question.
    """

    user_id = update.message.from_user.id

    # Save correct answer in userDict
    userDict[user_id]['answer'] = update.message.text

    # Try to init question instance
    QuestionType = userDict[user_id]['questtype']
    try:
        userDict[user_id]['questionInstance'] = QuestionType(userDict[user_id]['question'],
                                                             userDict[user_id]['answer'])
    except AssertionError:
        # TODO specify exceptions
        # Error because it isnt a number, no entry, not True/False,...
        update.message.reply_text(
            "Sorry. Something went wrong by entering your answer. Please try again. 😕")
        logger.info('[%s] Entering correct answer "%s" failed',
                    update.message.from_user.username, update.message.text)
        return 'ENTER_ANSWER'

    logger.info('[%s] Entering correct answer "%s" accepted',
                update.message.from_user.username, update.message.text)

    if isinstance(userDict[user_id]['questionInstance'], QuestionChoice):
        # If QuestionChoice instance, ask for additional possible answers
        update.message.reply_text(
            "Please enter additional possible answers separated by ', ' 😁")
        return 'ENTER_POSSIBLE_ANSWER'

    # Add question to quiz
    userDict[user_id]['quiz'].add_question(
        userDict[user_id]['questionInstance'])

    # Asks for type of next question
    list_question = [[el] for el in list(dict_question_types.keys())]
    update.message.reply_text(
        "What type of question should the next one be? "
        "If you don't have more questions, press 'Enter'.",
        reply_markup=ReplyKeyboardMarkup(
            list_question + [['Enter']], one_time_keyboard=True)
    )
    return 'ENTER_TYPE'


def enter_possible_answer(update, _):
    """
    After entering additional possible answers, it asks whether the order of the answers
    should be random.
    """

    user_id = update.message.from_user.id
    list_possible_answers = update.message.text.split(', ')
    # Add possible answers to question
    for answer in list_possible_answers:
        userDict[user_id]['questionInstance'].add_possible_answer(answer)

    logger.info('[%s] Entered additional possible answers',
                update.message.from_user.username)

    # Ask for
    update.message.reply_text(
        "Should the answers be displayed in random order? 🤔",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RANDOMNESS_QUESTION'


def enter_randomness_question(update, _):
    """
    After entering whether the order if the answers should be random,
    it adds the question to the quiz.
    After that, it asks for the type of next question.
    """
    user_id = update.message.from_user.id

    # Check for correct input
    if not update.message.text in ('Yes', 'No'):
        update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the answers be displayed in random order?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RANDOMNESS_QUESTION'

    userDict[user_id]['questionInstance'].is_random = update.message.text == 'Yes'
    logger.info('[%s] Entered randomness of the order of possible answers',
                update.message.from_user.username)

    # Add question to quiz
    userDict[user_id]['quiz'].add_question(
        userDict[user_id]['questionInstance'])
    logger.info('[%s] Added the question to the quiz',
                update.message.from_user.username)

    # Asks for type of next question
    list_question = [[el] for el in list(dict_question_types.keys())]
    update.message.reply_text(
        "What type of question should the next one be? "
        "If you don't have more questions, press 'Enter'.",
        reply_markup=ReplyKeyboardMarkup(
            list_question + [['Enter']], one_time_keyboard=True)
    )
    return 'ENTER_TYPE'


def enter_randomness_quiz(update, _):
    """
    After entering whether the order if the questions should be random,
    it asks if the result of the question be displayed after the question itself.
    """
    user_id = update.message.from_user.id

    # Check for correct input
    if not update.message.text in ('Yes', 'No'):
        update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the questions be displayed in random order?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RANDOMNESS_QUIZ'

    # Process input
    userDict[user_id]['quiz'].is_random = update.message.text == 'Yes'

    # Ask for displaying result after question
    update.message.reply_text(
        "Should the result of the question be displayed after the question?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RESULT_AFTER_QUESTION'


def enter_result_after_question(update, _):
    """
    After entering whether the result of the question should be displayed after the question itself,
    it asks if the result of every question be displayed after the quiz.
    """
    user_id = update.message.from_user.id

    # Check for correct input
    if not update.message.text in ('Yes', 'No'):
        update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the result of the question be displayed after the question?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RESULT_AFTER_QUESTION'

    # Process input
    userDict[user_id]['quiz'].show_results_after_question = update.message.text == 'Yes'

    # Ask for displaying result of every question after quiz
    update.message.reply_text(
        "Should the result of every question be displayed after the quiz?",
        reply_markup=ReplyKeyboardMarkup(
            [['Yes', 'No']], one_time_keyboard=True)
    )

    return 'ENTER_RESULT_AFTER_QUIZ'


def enter_result_after_quiz(update, _):
    """
    After entering whether the result of every question should be displayed after the quiz,
    it asks for the name of the quiz?
    """
    user_id = update.message.from_user.id

    # Check for correct input
    if not update.message.text in ('Yes', 'No'):
        update.message.reply_text(
            "Thats not a 'Yes' or a 'No' 😕"
            "Should the result of every question be displayed after the quiz?",
            reply_markup=ReplyKeyboardMarkup(
                [['Yes', 'No']], one_time_keyboard=True)
        )
        return 'ENTER_RESULT_AFTER_QUIZ'

    # Process input
    userDict[user_id]['quiz'].show_results_after_quiz = update.message.text == 'Yes'

    # Ask for name of quiz
    update.message.reply_text(
        "Great! 😃 I created a new quiz!\nHow should I name it? ✏️"
    )

    return 'ENTER_QUIZ_NAME'


def enter_quiz_name(update, context):
    """
    After entering the name of the quiz, it looks up if the quiz name is occupied.
    Otherwise is saves the quiz.
    """

    logger.info('[%s] Completed quiz creation',
                update.message.from_user.username)
    user_id = update.message.from_user.id
    quizname = update.message.text

    # Bot is typing during database query
    context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)

    # Query for question with input name
    user_col = db[update.message.from_user.username]
    if not user_col.find_one({'quizname': quizname}) is None:
        # Quiz with quizname already exists
        update.message.reply_text(
            "Sorry. You already have a quiz named {} 😕\nPlease try something else".format(
                quizname)
        )
        logger.info('[%s] Quiz with name "%s" already exists',
                    update.message.from_user.username, update.message.text)

        return 'ENTER_QUIZ_NAME'

    # Insert Quiz with quizname in database
    user_col.insert_one(
        {'quizname': quizname, 'quizinstance': pickle.dumps(userDict[user_id]['quiz'])})
    update.message.reply_text(
        "Great! 🥳 I saved your new quiz."
        "You can attempt to it by the name {}.".format(quizname),
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info('[%s] Quiz saved as "%s"',
                update.message.from_user.username, update.message.text)
    # Delete user data
    userDict.pop(update.message.from_user.id)
    return ConversationHandler.END
