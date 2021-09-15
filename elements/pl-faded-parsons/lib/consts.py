from typing import *

from os.path import join
from re import compile, Pattern

class Bcolors:
    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    HEADER: Final[str] = '\033[95m'
    OKBLUE: Final[str] = '\033[94m'
    OKCYAN: Final[str] = '\033[96m'
    OKGREEN: Final[str] = '\033[92m'
    WARNING: Final[str] = '\033[93m'
    FAIL: Final[str] = '\033[91m'
    ENDC: Final[str] = '\033[0m'
    BOLD: Final[str] = '\033[1m'
    UNDERLINE: Final[str] = '\033[4m'

    @staticmethod
    def f(color: str, *args, sep=' '):
        return color + sep.join(map(str, args)) + Bcolors.ENDC

    @staticmethod
    def printf(color: str, *args, **kwargs):
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


TEST_DEFAULT: Final[str] = """# AUTO-GENERATED FILE
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

SETUP_CODE_DEFAULT: Final[str] = """# AUTO-GENERATED FILE
# go to https://prairielearn.readthedocs.io/en/latest/python-grader/#testssetup_codepy for more info\n"""

SERVER_DEFAULT: Final[str] = """# AUTO-GENERATED FILE
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
MAIN_PATTERN: Final[Pattern] = compile(
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

SPECIAL_COMMENT_PATTERN: Final[Pattern] = compile(r'^#(blank[^#]*|\d+given)\s*')

BLANK_SUBSTITUTE: Final[str] = '!BLANK'

SPECIAL_REGIONS: Final[str] = {
    'setup': join('test', 'setup_code.py'),
    'setup_code': join('test', 'setup_code.py'),
    'ans': join('test', 'ans.py'),
    'answer': join('test', 'ans.py'),
    'answer_code': join('test', 'ans.py'),
    'question': 'question_text',
    'question_code': 'question_text'
}

PROGRAM_DESCRIPTION: Final[str] = Bcolors.f(Bcolors.OKGREEN, ' A tool for generating faded parsons problems.') + """

 Provide the path to well-formatted python file(s), and a question template will be generated.
 This tool will search for a path in ./ questions/ ../../questions/ and ../../ before erring.
 If none is provided, it will hunt for a questions directory, and use all .py files there.
 """ + Bcolors.f(Bcolors.OKBLUE, 'Formatting rules:') + """
 - If the file begins with a docstring, it will become the question text
     - The question text is removed from the answer
     - Docstrings are always removed from the prompt
 - Text surrounded by `?`s will become blanks in the prompt
     - Blanks cannot span more than a single line
     - The text within the question marks fills the blank in the answer
     - `?`s in any kind of string-literal or comment are ignored
 - Comments are removed from the prompt unless the comment matches the form `#{n}given` or `#blank`
     - These special forms are the only comments removed from the answer
 - Regions are begun and ended by `## {region name} ##`
     - A maximum of one region may be open at a time
     - Regions must be closed before the end of the source
     - All text in a region is only copied into that region
     - Text will be copied into a new file with the regions name in the
       question directory, excluding these special regions:
         explicit: `test` `setup_code`
         implicit: `answer_code` `prompt_code` `question_text`
     - Code in `setup_code` will be parsed to extract exposed names unless the --no-parse
       flag is set. Type annotations and function docstrings are used to fill out server.py
     - Any custom region that clashes with an automatically generated file name
       will overwrite the automatically generated code"""
