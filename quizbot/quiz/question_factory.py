"""
With this module, you can create questions different kinds.
"""


class Question:
    """
    General class for questions.
    """

    def __init__(self, question, correct_answer):
        """
        Initialize a question by the question and the correct answer.
        Additionally, it initializes the user answer as an empty string.

        :param question: Question of the question-instance as string.
        :param correct_answer: Correct answer of the question in (question specific) type.
        :raises AssertionError: If the question or the correct answer is empty.
        """
        assert question and correct_answer
        self.question = question
        self.correct_answer = correct_answer
        self.user_answer = str()

    def check_solution(self):
        """
        Checks the entered solution of the user with the correct answer.

        :returns: Boolean value whether the entered solution equals the correct answer.
        :raises AssertionError: No solution was entered by the user yet.
        """
        assert self.user_answer

    def enter_solution(self, answer):
        """
        Enters the answer by the user.

        :param answer: Answer by the user as a string.
        """
        self.user_answer = answer


class QuestionNumber(Question):
    """
    Subclass for questions with an integer as answer.
    Inherits from question.
    """

    def __init__(self, question, correct_answer):
        """
        Initialize a question by the question and the correct answer.
        Additionally, it initializes the user answer as an empty string.

        :param question: Question of the question-instance as string.
        :param correct_answer: Correct answer of the question as number.
        :raises AssertionError: If the question or the correct answer is not a number.
        """
        assert correct_answer.replace('.', '', 1).isdigit()
        super().__init__(question, correct_answer)

    def enter_solution(self, answer):
        """
        Enters the answer by the user.

        :param answer: Answer by the user as a string.
        :raises ValueError: If answer is not an integer.
        """
        assert answer.replace('.', '', 1).isdigit()
        return super().enter_solution(answer)

    def check_solution(self):
        """
        Compares the entered answer by the user with the correct number.

        :returns: Boolean value whether the entered number equals the correct number.
        :raises AssertionError: If no solution was entered by the user yet.
        """
        super().check_solution()
        # TODO add accuracy
        return abs(float(self.user_answer) - float(self.correct_answer)) < 0.00001


class QuestionString(Question):
    """
    Subclass for questions with a string as answer.
    Inherits by question.
    """

    def check_solution(self):
        """
        Checks the entered answer of the user with the correct string.

        :returns: Boolean value whether the entered string equals the correct string.
        :raises AssertionError: If no solution was entered by the user yet.
        """
        super().check_solution()
        return self.user_answer == self.correct_answer


class QuestionBool(Question):
    """
    Subclass for questions with a boolean value as answer.
    Inherits by question.
    """

    def __init__(self, question, correct_answer):
        """
        Initialize a question by the question and the correct answer.
        Additionally, it initializes the user answer as an empty string.

        :param question: Question of the question-instance as string.
        :param correct_answer: Correct answer of the question as boolean value (True or False).
        :raises AssertionError: If the question or the correct answer is not a boolean value.
        """
        assert correct_answer in ('True', 'False')
        super().__init__(question, correct_answer)

    def enter_solution(self, answer):
        """
        Enters the users' answer.

        :param answer: Answer by the user as a string.
        :raises AssertionError: If the entered answer isn't "True" or "False"
        """
        assert answer in ("True", "False")
        return super().enter_solution(answer)

    def check_solution(self):
        """
        Compares the entered answer by the user with the correct boolean value.

        :returns: Boolean value whether the entered value equals the correct value.
        :raises AssertionError: If no solution was entered by the user yet.
        """
        super().check_solution()
        return self.user_answer == self.correct_answer


class QuestionChoice(Question):
    """
    Subclass for questions with multiple possible and correct answers.
    Inherits by question.
    """

    def __init__(self, question, correct_answer):
        """
        Initialize a question by the question and the correct answer.
        Additionally, it initializes the user answer as an empty string,
        the randomness as False and the list of possible answers as a list of correct answers.

        :param question: Question of the question-instance as string.
        :param correct_answer: Correct answers of the question as string (seperated by comma).
        :raises AssertionError: If the question is empty
            or the count of correct answers is smaller than one.
        """
        assert correct_answer
        super().__init__(question, correct_answer)
        self.is_random = False
        self.possible_answers = correct_answer.split(', ')

    def add_possible_answer(self, new_answer):
        """
        Adds an answer to the list of possible answers.

        :param new_answer: New answer in the list of possible answers as string.
        """
        assert not new_answer in self.possible_answers
        self.possible_answers.append(new_answer)

    def check_solution(self):
        """
        Checks if the intersection of the list of entered answers
        and the list of correct answers equals the entered answers.

        :returns: Boolean value if the entered values equals the correct values.
        :raises AssertionError: If no solution was entered by the user yet.
        """
        super().check_solution()
        return set(self.user_answer.split(", ")) == set(self.correct_answer.split(", "))


class QuestionChoiceSingle(QuestionChoice):
    """
    Subclass for questions with multiple possible and correct answers.
    Inherits by question_choice.
    """

    def __init__(self, question="", correct_answer=""):
        """
        Initialize a question by the question and the correct answer.
        Additionally, it initializes the user answer as an empty string,
        the randomness as False and the list of possible answers as an empty list.

        :param question: Question of the question-instance as string.
        :param correct_answer: Correct answers of the question as list.
        :raises AssertionError: If the question is empty
            or the count of correct answers doesn't equal one.
        """
        assert len(correct_answer.split(", ")) == 1
        super().__init__(question, correct_answer)

    def enter_solution(self, answer):
        """
        Enters the answer by the user.

        :param answer: Answer by the user as a string.
        :raises AssertionError: If the entered string includes more than one answer.
        """
        assert len(answer.split(", ")) == 1
        return super().enter_solution(answer)
