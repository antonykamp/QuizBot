"""
With this module, you can create quizzes with questions different kinds.
"""

from quizbot.quiz.question_factory import Question


class Quiz:
    """
    An Instance of the class Quiz has a list of questions, which defines the Quiz.
    You can choose whether
        - the order of the questions is random
        - the result of the entered answer is shown after the question
        - the result of the entered answer of every question is shown after the quiz
    """

    def __init__(self, author="") -> None:
        """
        Initializes an instance of the class Quiz.

        :param author: Author of the quiz
        """
        self.questions = []
        self.is_random = False
        self.author = author
        self.show_results_after_quiz = True
        self.show_results_after_question = True

    def add_question(self, new_question: Question):
        """
        Add an instance of the class Question to the list of questions.

        :param new_question: New question of the quiz.
        """
        self.questions.append(new_question)

    def get_questions(self):
        """
        Returns a copy of the list of questions.

        :returns: List of questions.
        """
        return self.questions.copy()
