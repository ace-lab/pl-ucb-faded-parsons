from typing import *

from os.path import join
from re import compile

class Bcolors:
    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    HEADER: Final = '\033[95m'
    OKBLUE: Final = '\033[94m'
    OKCYAN: Final = '\033[96m'
    OKGREEN: Final = '\033[92m'
    WARNING: Final = '\033[93m'
    FAIL: Final = '\033[91m'
    ENDC: Final = '\033[0m'
    BOLD: Final = '\033[1m'
    UNDERLINE: Final = '\033[4m'

    @staticmethod
    def f(color, *args, sep=' '):
        return color + sep.join(map(str, args)) + Bcolors.ENDC

    @staticmethod
    def printf(color, *args, **kwargs):
        sep = ' '
        if 'sep' in kwargs:
            sep = kwargs['sep']
            del kwargs['sep']
        print(Bcolors.f(color, *args, sep=sep), **kwargs)

    @staticmethod
    def warn(*args, **kwargs):
        Bcolors.printf(Bcolors.WARNING, *args, **kwargs)

    @staticmethod
    def fail(*args, **kwargs):
        Bcolors.printf(Bcolors.FAIL, *args, **kwargs)


TEST_DEFAULT: Final = """# AUTO-GENERATED FILE
# go to https://prairielearn.readthedocs.io/en/latest/python-grader/#teststestpy for more info

from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback


class Test(PLTestCase):
    @points(1)
    @name("test 0")
    def test_0(self):
        points = 0
        # ex: calling a student defined function det 
        #     with args=(1, 2, 3, 4)
        # case = [1, 2, 3, 4]
        # user_val = Feedback.call_user(self.st.det, *case)

        # ex: calling a function defined in ans.py called det
        #     with the same arguments
        # ref_val = self.ref.det(*case)

        # ex: test correctness, update points
        # if Feedback.check_scalar('case: ' + case, ref_val, user_val):
        #     points += 1
        
        Feedback.set_score(points)\n"""

SETUP_CODE_DEFAULT: Final = """# AUTO-GENERATED FILE
# go to https://prairielearn.readthedocs.io/en/latest/python-grader/#testssetup_codepy for more info\n"""

SERVER_DEFAULT: Final = """# AUTO-GENERATED FILE
# go to https://prairielearn.readthedocs.io/en/latest/python-grader/#serverpy for more info

def generate(data):
    # Define incoming variables here
    names_for_user = [
        # ex: student recieves a matrix m
        # {"name": "m", "description": "a 2x2 matrix", "type": "numpy array"}
    ]
    # Define outgoing variables here
    names_from_user = [
        # ex: student defines a determinant function name det
        # {"name": "det", "description": "determinant for a 2x2 matrix", "type": "python function"}
    ]

    data["params"]["names_for_user"] = names_for_user
    data["params"]["names_from_user"] = names_from_user

    return data\n"""

# Matches, with precedence in listed order:
MAIN_PATTERN: Final = compile(
    # - capture group 0: (one-line) region delimiter surrounded by ##'s
    #                    (capturing only the text between the ##'s).
    #                    Consumes leading newline and surrounding spaces/tabs,
    #                    and if the next line doesn't have a region comment,
    #                    it consumes the trailing newline as well.
    r'(?:\r?\n|^)[ \t]*\#\#[\t ]*(.*?)\s*\#\#.*?(?:(?=\r?\n[ \t]*\#\#)|\r?\n|$)|' +
    # - capture group 1:  (one-line) comment, up to next comment or newline 
    #                     (excluding the newline/eof)
    r'(\#.*?)(?=\#|\r?\n|$)|' +
    # - capture group 2: (multi-line) triple-quote string literal
    r'(\"\"\"[\s\S]*?\"\"\")|' + 
    # - capture group 3:
    #     - (one-line) single-apostrophe string literal
    #     - (one-line) single-quote string literal
    r'(\'.*?\'|\".*?\")|' + 
    # - capture group 4:  (one-line) answer surrounded by ?'s (excluding ?'s)
    r'\?(.*?)\?'
)

SPECIAL_COMMENT_PATTERN: Final = compile(r'^#(blank[^#]*|\d+given)\s*')

BLANK_SUBSTITUTE: Final = '!BLANK'

SPECIAL_REGIONS: Final = {
    'setup': join('test', 'setup_code.py'),
    'setup_code': join('test', 'setup_code.py'),
    'ans': join('test', 'ans.py'),
    'answer': join('test', 'ans.py'),
    'answer_code': join('test', 'ans.py'),
    'question': 'question_text',
    'question_code': 'question_text'
}
