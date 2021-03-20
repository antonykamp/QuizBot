"""
This module tests the telegram bot by creating and attempting to a quiz.
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom.message import Message
from pytest import mark
import os
import pymongo

db = pymongo.MongoClient(os.environ.get('MONGODB')).quizzes
SESSION_STR = os.environ['SESSION_STR']
API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']


@mark.asyncio
async def test_complete_bot():
    """Tests the whole bot"""

    client = TelegramClient(StringSession(
        SESSION_STR), API_ID, API_HASH)
    await client.connect()
    async with client.conversation("antonystestbot", timeout=10) as conv:

        # Tests help command
        await conv.send_message("/help")
        resp = await conv.get_response()
        assert "Hey! 🙋‍♂️ How can I help you?" in resp.raw_text
        resp = await conv.get_response()
        assert "What QuizBot is? 😃" in resp.raw_text
        assert "With QuizBot you can create quizzes with different question types. 🧐 You can" in resp.raw_text
        assert "- ask for a number," in resp.raw_text
        assert "- ask for a string," in resp.raw_text
        assert "- ask für a boolean value," in resp.raw_text
        assert "- create multiple choice questions or" in resp.raw_text
        assert "- create multiple choice questions with one correct answer." in resp.raw_text
        assert "If you want to create a new quiz, call /create. 🤓" in resp.raw_text
        assert "If you want to attempt a quiz, call /attempt. 🤔" in resp.raw_text
        assert "If you want to rename one of your quizzes, call /rename. ✏️" in resp.raw_text
        assert "If you want to delete one of your quizzes, call /remove." in resp.raw_text
        assert "Have fun! 🥳" in resp.raw_text

        ############
        # CREATION #
        ############

        # Tests init createQuiz Process
        await conv.send_message("/create")
        resp = await conv.get_response()
        assert "Hi 😃 Let's create a new quiz!" in resp.raw_text
        assert "What type of question should the first one be?" in resp.raw_text
        assert "If you want to cancel your creation, enter /cancelCreate." in resp.raw_text

        # Tests asking for number
        await conv.send_message("Ask for a number")
        resp = await conv.get_response()
        assert "What is the question? 🤔" in resp.raw_text

        # Tests input question
        await conv.send_message("42?")
        resp = await conv.get_response()
        assert "Please enter the correct answer 🙆‍♂️" in resp.raw_text

        # Tests input wrong type as correct answer
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Sorry. Something went wrong by entering your answer. Please try again. 😕"\
            in resp.raw_text

        # Tests input correct answer
        await conv.send_message("42")
        resp = await conv.get_response()
        assert "What type of question should the next one be?" in resp.raw_text
        assert "If you don't have more questions, press 'Enter'." in resp.raw_text

        # Create question asking for String
        await conv.send_message("Ask for a string")
        await conv.get_response()

        # Input question
        await conv.send_message("Hello?")
        await conv.get_response()

        # Input correct answer
        await conv.send_message("Hello")
        await conv.get_response()

        # Creation question asking for boolean value
        await conv.send_message("Ask for a boolean value")
        await conv.get_response()

        # Input question
        await conv.send_message("True?")
        await conv.get_response()

        # Tests input wrong type as correct answer
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Sorry. Something went wrong by entering your answer. Please try again. 😕"\
            in resp.raw_text

        # Input correct answer
        await conv.send_message("True")
        await conv.get_response()

        # Create multiple choice question
        await conv.send_message("Ask a multiple choice question")
        await conv.get_response()

        # Tests input question of multiple choice question
        await conv.send_message("a, b?")
        resp = await conv.get_response()
        assert "Please enter the correct answers separated by ', ' 🙆‍♂️" in resp.raw_text

        # Tests input correct answer of mutiple choice question
        await conv.send_message("a, b")
        resp = await conv.get_response()
        assert "Please enter additional possible answers separated by ', ' 😁" in resp.raw_text

        # Input addition possible answers
        await conv.send_message("c, d, e")
        resp = await conv.get_response()
        assert "Should the answers be displayed in random order? 🤔" in resp.raw_text

        # Tests entering wrong type
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Thats not a 'Yes' or a 'No' 😕" in resp.raw_text
        assert "Should the answers be displayed in random order?" in resp.raw_text

        # Tests entering correct types
        await conv.send_message("Yes")
        resp = await conv.get_response()
        assert "What type of question should the next one be?" in resp.raw_text
        assert "If you don't have more questions, press 'Enter'." in resp.raw_text

        # Create multiple choice question with one correct answer
        await conv.send_message("Ask a multiple choice question with one correct answer")
        await conv.get_response()

        # Tests input question of multiple choice question with one correct answer
        await conv.send_message("a?")
        resp = await conv.get_response()
        assert "Please enter ONE correct answer ☝️" in resp.raw_text

        # Tests input more than one answer as correct answer
        await conv.send_message("a, b")
        resp = await conv.get_response()
        assert "Sorry. Something went wrong by entering your answer. Please try again. 😕"\
            in resp.raw_text

        # Input correct answer
        await conv.send_message("a")
        await conv.get_response()

        # Input additional possible answers
        await conv.send_message("b, c")
        resp = await conv.get_response()
        assert "Should the answers be displayed in random order? 🤔" in resp.raw_text

        # Tests entering wrong type
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Thats not a 'Yes' or a 'No' 😕" in resp.raw_text
        assert "Should the answers be displayed in random order?" in resp.raw_text

        # Tests entering correct types
        await conv.send_message("Yes")
        resp = await conv.get_response()
        assert "What type of question should the next one be?" in resp.raw_text
        assert "If you don't have more questions, press 'Enter'." in resp.raw_text

        # Tests enter quiz
        await conv.send_message("Enter")
        resp = await conv.get_response()
        assert "Should the questions be displayed in random order?" in resp.raw_text

        # Tests entering wrong type
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Thats not a 'Yes' or a 'No' 😕" in resp.raw_text
        assert "Should the questions be displayed in random order?" in resp.raw_text

        # Tests entering correct types
        await conv.send_message("No")
        resp = await conv.get_response()
        assert "Should the result of the question be displayed after the question?" in resp.raw_text

        # Tests entering wrong type
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Thats not a 'Yes' or a 'No' 😕" in resp.raw_text
        assert "Should the result of the question be displayed after the question?" in resp.raw_text

        # Tests entering correct types
        await conv.send_message("Yes")
        resp = await conv.get_response()
        assert "Should the result of every question be displayed after the quiz?" in resp.raw_text

        # Tests entering wrong type
        await conv.send_message("wrong enter")
        resp = await conv.get_response()
        assert "Thats not a 'Yes' or a 'No' 😕" in resp.raw_text
        assert "Should the result of every question be displayed after the quiz?" in resp.raw_text

        # Tests entering correct types
        await conv.send_message("Yes")
        resp = await conv.get_response()
        assert "Great! 😃 I created a new quiz!" in resp.raw_text
        assert "How should I name it? ✏️" in resp.raw_text

        # Tests input quizname
        await conv.send_message("unittestquiz")
        resp = await conv.get_response()
        assert "Great! 🥳 I saved your new quiz." in resp.raw_text
        assert "You can attempt to it by the name unittestquiz." in resp.raw_text

        ###########
        # ATTEMPT #
        ###########

        # Tests entering attempt
        await conv.send_message("/attempt")
        resp = await conv.get_response()
        assert 'Hi 😃 On which quiz do you want to participate in?' in resp.raw_text
        assert 'Please enter the name of the quiz.' in resp.raw_text
        assert "If the quiz wasn't created by you, please enter the username of the creator after that."\
            in resp.raw_text

        # Tests dont find entered quiz
        await conv.send_message("nothing")
        resp = await conv.get_response()
        assert "Sorry, I couldn't find the quiz 'nothing' 😕 Please try again." in resp.raw_text

        # Tests enter dummy test and first question
        await conv.send_message("unittestquiz")
        resp: Message = await conv.get_response()
        assert "Lets go! 🙌 Have fun with the quiz 'unittestquiz'!" in resp.raw_text
        assert 'You can cancel your participation with /cancelAttempt.' in resp.raw_text
        resp = await conv.get_response()
        assert '42?' in resp.raw_text

        # Tests answering QuestionNumber instance with string
        await conv.send_message("Hello")
        resp = await conv.get_response()
        assert "Sorry 😕 Something went wrong by entering your answer. Please try again."\
            in resp.raw_text

        # Tests answering QuestionNumber instance
        await conv.send_message("41")
        resp = await conv.get_response()
        assert "Sorry, thats not correct. 😕" in resp.raw_text
        assert "The correct answer is: 42" in resp.raw_text
        resp = await conv.get_response()
        assert "Hello?" in resp.raw_text

        # Tests answering QuestionString instance
        await conv.send_message("Hello")
        resp = await conv.get_response()
        assert "Thats correct 😁" in resp.raw_text
        resp = await conv.get_response()
        assert "True?" in resp.raw_text

        # Tests answering QuestionBool instance with string
        await conv.send_message("Hello")
        resp = await conv.get_response()
        assert "Sorry 😕 Something went wrong by entering your answer. Please try again."\
            in resp.raw_text

        # Tests answering QuestionBool instance
        await conv.send_message("True")
        resp = await conv.get_response()
        assert "Thats correct 😁" in resp.raw_text
        resp = await conv.get_response()
        assert "a, b?" in resp.raw_text

        # Tests answering QuestionChoice instance without entering any possible answer
        await conv.send_message("Enter")
        resp = await conv.get_response()
        assert "Sorry 😕 Something went wrong by entering your answer. Please try again."\
            in resp.raw_text

        # Tests answering QuestionChoice instance
        await conv.send_message("a")
        await conv.send_message("b")
        await conv.send_message("Enter")
        resp = await conv.get_response()
        assert "Thats correct 😁" in resp.raw_text
        resp = await conv.get_response()
        assert "a?" in resp.raw_text

        # Tests answering QuestionChoiceSingle instance
        await conv.send_message("a")
        resp = await conv.get_response()
        assert "Thats correct 😁" in resp.raw_text
        resp = await conv.get_response()
        assert "Thanks for your participation! ☺️" in resp.raw_text

        # Tests output after quiz
        resp = await conv.get_response()
        assert "Question 1:" in resp.raw_text
        assert "42?" in resp.raw_text
        assert "Your answer was wrong. 😕" in resp.raw_text
        assert "The correct answer is: 42" in resp.raw_text

        resp = await conv.get_response()
        assert "Question 2:" in resp.raw_text
        assert "Hello?" in resp.raw_text
        assert "Your answer was correct 😁" in resp.raw_text

        resp = await conv.get_response()
        assert "Question 3:" in resp.raw_text
        assert "True?" in resp.raw_text
        assert "Your answer was correct 😁" in resp.raw_text

        resp = await conv.get_response()
        assert "Question 4:" in resp.raw_text
        assert "a, b?" in resp.raw_text
        assert "Your answer was correct 😁" in resp.raw_text

        resp = await conv.get_response()
        assert "Question 5:" in resp.raw_text
        assert "a?" in resp.raw_text
        assert "Your answer was correct 😁" in resp.raw_text

        # Tests CancelAttempt command
        await conv.send_message("/attempt")
        await conv.get_response()
        await conv.send_message("unittestquiz antonykamp")
        await conv.get_response()
        await conv.get_response()
        await conv.send_message("/cancelAttempt")
        resp = await conv.get_response()
        assert "I canceled you attempt. See you next time. 🙋‍♂️" in resp.raw_text

        # Test quizname already exists
        await conv.send_message("/create")
        await conv.get_response()
        await conv.send_message("Ask for a string")
        await conv.get_response()
        await conv.send_message("Test?")
        await conv.get_response()
        await conv.send_message("Test!")
        await conv.get_response()
        await conv.send_message("Enter")
        await conv.get_response()
        await conv.send_message("Yes")
        await conv.get_response()
        await conv.send_message("Yes")
        await conv.get_response()
        await conv.send_message("Yes")
        await conv.get_response()
        await conv.send_message("unittestquiz")
        resp = await conv.get_response()
        assert "Sorry. You already have a quiz named unittestquiz 😕" in resp.raw_text
        assert "Please try something else" in resp.raw_text

        # Test cancel Create
        await conv.send_message("/cancelCreate")
        resp = await conv.get_response()
        assert "I canceled the creation process. See you next time. 🙋‍♂️" in resp.raw_text

        ##########
        # RENAME #
        ##########

        # Tests asking for renaming
        await conv.send_message("/rename")
        resp = await conv.get_response()
        assert "Which quiz do you want to rename? ✏️" in resp.raw_text

        # Tests asking for renaming nonexisiting quiz
        await conv.send_message("nothing")
        resp = await conv.get_response()
        assert "The quiz 'nothing' doesn't exist 😕" in resp.raw_text
        assert "Please try again or cancel process with /cancelEdit 🙆‍♂️" in resp.raw_text

        # Tests asking for renaming exisiting quiz
        await conv.send_message("unittestquiz")
        resp = await conv.get_response()
        assert "How should I name it? 🤔" in resp.raw_text

        # Tests asking for renaming to exisiting quiz
        await conv.send_message("unittestquiz")
        resp = await conv.get_response()
        assert "The quiz 'unittestquiz' already exists 😕" in resp.raw_text
        assert "Please try again or cancel process with /cancelEdit 🙆‍♂️" in resp.raw_text

        # Tests asking for renaming to nonexisiting quiz
        await conv.send_message("newname")
        resp = await conv.get_response()
        assert "I renamed 'unittestquiz' to 'newname' 🥳" in resp.raw_text

        ##########
        # REMOVE #
        ##########

        # Tests asking to remove quiz
        await conv.send_message("/remove")
        resp = await conv.get_response()
        assert "Which quiz do you want to delete? 🙂" in resp.raw_text

        # Tests asking for removing nonexisiting quiz
        await conv.send_message("unittestquiz")
        resp = await conv.get_response()
        assert "The quiz 'unittestquiz' doesn't exist 😕" in resp.raw_text
        assert "Please try again or cancel process with /cancelEdit 🙆‍♂️" in resp.raw_text

        # Tests asking for removing exisiting quiz
        await conv.send_message("newname")
        resp = await conv.get_response()
        assert "I deleted 'newname' 👍" in resp.raw_text

        # Checking existence of deleted quiz
        user_col = db['antonykamp']
        assert user_col.find_one({'quizname': 'newname'}) is None

        # Starts removing process
        await conv.send_message("/remove")
        resp = await conv.get_response()

        # Tests canceling removing process
        await conv.send_message("/cancelEdit")
        resp = await conv.get_response()
        assert "I canceled the editing process." in resp.raw_text

    await client.disconnect()
