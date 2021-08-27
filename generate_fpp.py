from typing import *
import re
from sys import argv
from os import makedirs, path, PathLike, write
from shutil import copyfile
from uuid import uuid4
from json import dumps

""" Matches, with precedence in listed order:
    - capture group 0
        - (one-line) comments (excluding the line-break terminator)
    - capture group 1
        - (one-line) single-apostrophe string literals
        - (multi-line) triple-quote string literals
        - (one-line) single-quote string literals
    - capture group 2
        - (one-line) answer surrounded by ?'s (excluding the ?'s)
"""
MAIN_PATTERN = re.compile(r'(\#.*?)(?=\r?\n)|(\'.*?\'|\"\"\"[\s\S]*?\"\"\"|\".*?\")|\?(.*?)\?')

SPECIAL_COMMENT_PATTERN = re.compile(r'^#\d+given')

BLANK_SUBSTITUTE = "!BLANK"

def extract_prompt_ans(source_code: str, keep_comments_in_prompt: bool = False) -> Tuple[str, str]:
    """ Extracts from one well-formatted `source_code` string the text for both
        the starting prompt and the answer text. Formatting rules:
            - Text that will be represented as blanks must be surrounded by `?`
            - Blanks cannot span more than a single line
            - `?`s in any kind of string-literal or comment are ignored
        
        Note: Empty lines are always stripped from the prompt. Comments are
        also removed by default, but setting `keep_comments_in_prompt` to True 
        will keep them in. Special comments of the kind `#{n}given` are always
        left inthe prompt and always removed from the answer.
            
        e.g.
        ```
        > source = "sum = lambda a, b: ?a + b? #0given"
        > extract_prompt_ans(source)
        ("sum = lambda a, b: !BLANK #0given", "sum = lambda a, b: a + b")

        > source = "?del bad?  # badness?!?"
        > extract_prompt_ans(source)
        ("!BLANK", "del bad  # badness?!?!")
        ```
    """
    prompt_code = ''
    answer_code = ''

    # (exclusive) end of the last match
    last_end = 0

    for match in re.finditer(MAIN_PATTERN, source_code):
        start, end = match.span()
       
        # make sure to keep uncaptured text between matches
        # (if no uncaptured text exists, unmatched = '')
        unmatched = source_code[last_end:start]
        prompt_code += unmatched
        answer_code += unmatched
        
        last_end = end
        
        # only one of these is ever non-None
        comment, string, blank_ans = match.groups()
        
        if comment:
            special_comment = re.match(SPECIAL_COMMENT_PATTERN, comment)

            if not special_comment:
                answer_code += comment

            if special_comment or keep_comments_in_prompt:
                # even if excluding the comment from the prompt,
                # every comment ends with a '\n'.
                # must keep it to maintain whitespacing
                prompt_code += comment
        elif string:
            # strings always stay in both
            prompt_code += string
            answer_code += string
        elif blank_ans:
            # fill in proper blank text
            prompt_code += BLANK_SUBSTITUTE
            answer_code += blank_ans
        else:
            raise Exception('All capture groups are None after', last_end)

    # don't forget everything after the last match!
    unmatched = source_code[last_end:]
    prompt_code += unmatched
    answer_code += unmatched
    
    # remove all whitespace-only lines 
    # usually as a result of removing comments)
    # then remove all indentation
    prompt_code = '\n'.join(filter(bool, map(str.strip, prompt_code.splitlines())))

    return prompt_code, answer_code

def generate_question_html(prompt_code: str, tab='  ') -> str:
    """Turn an extracted prompt string into a question html file body"""
    indented = prompt_code.replace('\n', '\n' + tab)
    return """
<pl-question-panel>
{tab}<!-- Write the question prompt here -->
</pl-question-panel>

<!-- AUTO-GENERATED QUESTION -->
<!-- see README for where the various parts of question live -->
<pl-faded-parsons>
{tab}{indented}
</pl-faded-parsons>
""".format(tab=tab, indented=indented).strip()

def filename(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the basename in the path without the file extensions"""
    return path.splitext(path.basename(file_path))[0]

def generate_fpp_question(source_path: PathLike[AnyStr]):
    """ Takes a path of a well-formatted source (see `extract_prompt_ans`),
        then generates and populates a question directory of the same name.
    """
    print('- Extracting from source...')
    with open(source_path, 'r') as source:
        source_code = ''.join(source)
        prompt_code, answer_code = extract_prompt_ans(source_code)
    
    question_dir = filename(source_path)

    print('- Creating destination directories')
    test_dir = path.join(question_dir, 'tests')
    makedirs(test_dir, exist_ok=True)

    print('- Copying source file...')
    copyfile(source_path, path.join(question_dir, 'source.py'))

    def write_to_dir(file_path: PathLike[AnyStr], data: AnyStr):
        with open(file_path, 'w+') as f:
            f.write(data)

    def write_to_question_dir(file_name: PathLike[AnyStr], data: AnyStr):
        write_to_dir(path.join(question_dir, file_name), data)

    def write_to_test_dir(file_name: PathLike[AnyStr], data: AnyStr):
        write_to_dir(path.join(test_dir, file_name), data)
    
    print('- Populating test directory...')
    write_to_test_dir('ans.py', answer_code)
    
    write_to_test_dir('setup_code.py', '# AUTO-GENERATED FILE\n')

    write_to_test_dir('test.py', """# AUTO-GENERATED FILE
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
        
        Feedback.set_score(points)\n""")
    
    print('- Populating {} directory...'.format(question_dir))
    write_to_question_dir('question.html', generate_question_html(prompt_code))

    write_to_question_dir('server.py',  """# AUTO-GENERATED FILE
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

    return data\n""")
    
    question_title = ' '.join(l.capitalize() for l in question_dir.split('_'))
    
    info_json = {
        'uuid': uuid4().hex,
        'title': question_title,
        'topic': '',
        'tags': ['berkeley', 'fp'],
        'type': 'v3',
        'gradingMethod': 'External',
        'externalGradingOptions': {
            'enabled': True,
            'image': 'prairielearn/grader-python',
            'entrypoint': '/python_autograder/run.sh'
        }
    }

    write_to_question_dir('info.json', dumps(info_json, indent=4) + '\n')


if __name__ == '__main__':
    if len(argv) < 2:
        raise Exception('Please provide a source code path as a first CLI argument')
    
    source_path = argv[1]

    print('Generating from source', source_path)    

    generate_fpp_question(source_path)

    print('Done.')


        
