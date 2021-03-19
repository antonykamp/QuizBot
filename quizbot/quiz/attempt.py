"""
With this module you can create one attemp of a quiz.
"""
import random
from quizbot.quiz.quiz import Quiz


class Attempt:
    """
    An Instance of the class Attempt has a quiz and a list of the left questions.
    """

    def __init__(self, quiz: Quiz) -> None:
        """
        Initializes an instance of the class Attempt.
        It shuffeles the question if the quiz specifies it.

        :param quiz: Quiz which wants the user to attempt.
        """
        self.quiz = quiz
        self.questions = quiz.get_questions()
        self.user_points = list()
        self.user_answers = set()
        if quiz.is_random:
            random.shuffle(self.questions)

    def has_next_question(self):
        """
        Checks if a question is left.

        :returns: If a question is left.
        """
        return not (len(self.questions)) == 0

    def act_question(self):
        """
        Returns the current question.

        :returns: Current question.
        """
        return self.questions[0]

    def input_answer(self, user_answer):
        """
        Enter one user answer.

        :param user_answer: A answer by the user
        """
        self.user_answers.add(user_answer)

    def enter_answer(self):
        """
        Checks the users' answer and removes the current question from the list.

        :returns: A pair of a boolean value whether the user answer was correct
            and the correct answer.
        """
        self.act_question().enter_solution(', '.join(self.user_answers))
        self.user_answers.clear()
        return_value = (self.act_question().check_solution(),
                        self.act_question().correct_answer)
        self.user_points.append((return_value[0], self.questions.pop(0)))
        return return_value
