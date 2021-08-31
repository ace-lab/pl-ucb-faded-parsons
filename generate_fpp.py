from collections import defaultdict
from typing import *
from re import compile, finditer, match as test
from os import makedirs, path, PathLike
from shutil import copyfile
from uuid import uuid4
from json import dumps
from enum import Enum, unique

class Bcolors(Enum):
    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def f(color, *args, sep=' '):
        return color.value + sep.join(map(str, args)) + Bcolors.ENDC.value

    @staticmethod
    def printf(color, *args, **kwargs):
        sep = ' '
        if 'sep' in kwargs:
            sep = kwargs['sep']
            del kwargs['sep']
        print(Bcolors.f(color, *args, sep=sep), **kwargs)


TEST_FILE_TEXT = """# AUTO-GENERATED FILE
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

SETUP_CODE_FILE_TEXT = '# AUTO-GENERATED FILE\n'

SERVER_FILE_TEXT = """# AUTO-GENERATED FILE
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
MAIN_PATTERN = compile(
# - capture group 0: (one-line) region delimiter surrounded by ##'s (excluding the ##'s and newline/eof)
    r'\s*\#\#\s*(.*?)\s*\#\#\s*(?=\#|\r?\n|$)|' +
# - capture group 1:  (one-line) comment, up to next comment or newline (excluding the newline/eof)
    r'(\#.*?)(?=\#|\r?\n|$)|' +
# - capture group 2: (multi-line) triple-quote string literal
    r'(\"\"\"[\s\S]*?\"\"\")|' + 
# - capture group 3:
#     - (one-line) single-apostrophe string literal
#     - (one-line) single-quote string literal
    r'(\'.*?\'|\".*?\")|' + 
# - capture group 4:  (one-line) answer surrounded by ?'s (excluding the ?'s)
    r'\?(.*?)\?'
)

SPECIAL_COMMENT_PATTERN = compile(r'^#(blank[^#]*|\d+given)\s*')

# capture group: region name
REGION_COMMENT_PATTERN = compile(r'')

BLANK_SUBSTITUTE = '!BLANK'

def extract_prompt_ans(
    source_code: str, 
    keep_comments_in_prompt: bool = False
    ) -> Tuple[str, str, str]:
    """ Extracts from one well-formatted `source_code` string the text for:

        0) the question text
        1) the starting prompt 
        2) the answer text

        Formatting rules:
        - If the file begins with a docstring, it will become the question text
            - The question text is removed from the answer
            - Docstrings are always removed from the prompt
        - Text surrounded by `?`s will become blanks in the prompt
            - Blanks cannot span more than a single line
            - The text within the question marks fills the blank in the answer
            - `?`s in any kind of string-literal or comment are ignored
        - Comments are removed from the prompt *unless*
            - `keep_comments_in_prompt = True` OR
            - The comment is of the form `#{n}given` or `#blank`, 
              which are the only comments removed from the answer
        
            
        e.g.
        ```
        > source = "sum = lambda a, b: ?a + b? #0given"
        > extract_prompt_ans(source)
        (None, "sum = lambda a, b: !BLANK #0given", "sum = lambda a, b: a + b")

        > source = "\\\"\\\"\\\"Make good?\\\"\\\"\\\" ?del bad?  # badness?!?"
        > extract_prompt_ans(source)
        ("Make good?", "!BLANK", "del bad  # badness?!?!")
        ```
    """
    question_text = None
    prompt_code = ''
    answer_code = ''

    # (exclusive) end of the last match
    last_end = 0
    first_match = True
    
    regions = defaultdict(str)
    current_region = None

    for match in finditer(MAIN_PATTERN, source_code):
        start, end = match.span()
       
        # make sure to keep uncaptured text between matches
        # (if no uncaptured text exists, unmatched = '')
        unmatched = source_code[last_end:start]
        if current_region:
            regions[current_region] += unmatched
        else:
            prompt_code += unmatched
            answer_code += unmatched
        
        last_end = end
        
        # only one of these is ever non-None
        region_delim, comment, docstring, string, blank_ans = match.groups()
        
        if region_delim:
            if current_region:
                if region_delim != current_region:
                    raise SyntaxError("Region \"{}\" began before \"{}\" ended".format(region_delim, current_region))
                else:
                    current_region = None
            else:
                current_region = region_delim
        elif current_region:
            regions[current_region] += next(filter(bool, match.groups()))
        elif comment:
            special_comment = test(SPECIAL_COMMENT_PATTERN, comment)

            if not special_comment:
                answer_code += comment

            if special_comment or keep_comments_in_prompt:
                # even if excluding the comment from the prompt,
                # every comment ends with a '\n'.
                # must keep it to maintain whitespacing
                prompt_code += comment
        elif docstring:
            if first_match:
                # isolate the question doc
                question_text = docstring[3:-3]
            else:
                # docstrings cannot be included in current FPP
                # prompt_code += docstring
                answer_code += docstring
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
        
        first_match = False

    # all region delimiters should've been detected.
    # if there's a current region, it'll never be closed
    if current_region:
        raise SyntaxError("File ended before \"" + current_region + "\" ended")

    # don't forget everything after the last match!
    unmatched = source_code[last_end:]
    prompt_code += unmatched
    answer_code += unmatched
    
    # remove all whitespace-only lines 
    # usually as a result of removing comments)
    # then remove all indentation
    prompt_code = '\n'.join(filter(bool, map(str.strip, prompt_code.splitlines())))

    print(regions)

    return question_text, prompt_code, answer_code

def generate_question_html(prompt_code: str, question_text: str = None, tab='  ') -> str:
    """Turn an extracted prompt string into a question html file body"""
    indented = prompt_code.replace('\n', '\n' + tab)
    
    if question_text is None:
        question_text = tab + '<!-- Write the question prompt here -->'
    
    return """<!-- AUTO-GENERATED FILE -->
<pl-question-panel>
{question_text}
</pl-question-panel>

<!-- see README for where the various parts of question live -->
<pl-faded-parsons>
{tab}{indented}
</pl-faded-parsons>""".format(question_text=question_text, tab=tab, indented=indented)

def generate_info_json(question_name: str, indent=4) -> str:
    """ Creates the default info.json for a new FPP question, with a unique v4 UUID.
        Expects `question_name` to be lower snake case.
    """
    question_title = ' '.join(l.capitalize() for l in question_name.split('_'))

    info_json = {
        'uuid': str(uuid4()),
        'title': question_title,
        'topic': '',
        'tags': ['berkeley', 'fp'],
        'type': 'v3',
        'gradingMethod': 'External',
        'externalGradingOptions': {
            'enabled': True,
            'image': 'prairielearn/grader-python',
            'entrypoint': '/python_autograder/run.sh',
            'timeout': 5
        }
    }

    return dumps(info_json, indent=indent) + '\n'

def filename(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the basename in the path without the file extensions"""
    return path.splitext(path.basename(file_path))[0]

def write_to(parent_dir: PathLike[AnyStr], file_path: PathLike[AnyStr], data: str):
    with open(path.join(parent_dir, file_path), 'w+') as f:
        f.write(data)

def generate_fpp_question(source_path: PathLike[AnyStr], force_generate_json: bool = False):
    """ Takes a path of a well-formatted source (see `extract_prompt_ans`),
        then generates and populates a question directory of the same name.
    """
    Bcolors.printf(Bcolors.OKBLUE, 'Generating from source', source_path)

    print('- Extracting from source...')
    with open(source_path, 'r') as source:
        source_code = ''.join(source)
        question_text, prompt_code, answer_code = extract_prompt_ans(source_code)
    
    question_name = filename(source_path)

    # create all new content in a new folder that is a
    # sibling of the source file in the filesystem
    question_dir = path.join(path.dirname(source_path), question_name)

    print('- Creating destination directories...')
    test_dir = path.join(question_dir, 'tests')
    makedirs(test_dir, exist_ok=True)


    copy_dest_path = path.join(question_dir, 'source.py')
    print('- Copying {} to {} ...'.format(path.basename(source_path), copy_dest_path))
    copyfile(source_path, copy_dest_path)


    print('- Populating {} ...'.format(question_dir))
    
    question_html = generate_question_html(prompt_code, question_text=question_text)
    write_to(question_dir, 'question.html', question_html)
    
    json_path = path.join(question_dir, 'info.json')
    if force_generate_json or not path.exists(json_path):
        write_to(question_dir, 'info.json', generate_info_json(question_name))
        Bcolors.printf(Bcolors.WARNING, '  - Overwriting', json_path, '...')

    write_to(question_dir, 'server.py',  SERVER_FILE_TEXT)
    

    print('- Populating {} ...'.format(test_dir))

    write_to(test_dir, 'ans.py', answer_code)
    
    write_to(test_dir, 'setup_code.py', SETUP_CODE_FILE_TEXT)

    write_to(test_dir, 'test.py', TEST_FILE_TEXT)
    

    Bcolors.printf(Bcolors.OKGREEN, 'Done.')

def generate_many(args: list[str]):
    if not args:
        raise Exception('Please provide at least one source code path as an argument')

    force_json = False
    files = 0
    for source_path in args:
        if source_path.startswith('--'):
            if source_path.endswith('force-json'):
                force_json = True
            else:
                Bcolors.printf(Bcolors.WARNING, '-', source_path, 
                    'not recognized as a flag! use --help for more info. -')
            continue
        
        if not path.exists(source_path):
            original = source_path
            source_path = path.join('questions', source_path)
            if not path.exists(source_path):
                raise FileNotFoundError('Could not find file at {} or {}.'.format(original, source_path))
            else:
                Bcolors.printf(Bcolors.WARNING, '- Could not find', original, 
                    'in current directory. Proceeding with detected file. -')

        generate_fpp_question(source_path, force_generate_json=force_json)
        files += 1
        force_json = False
    
    if len(args) > 2:
        Bcolors.printf(Bcolors.OKGREEN, 'Batch completed successfullly on', files, 'files.')

def profile_generate_many(args: list[str]):
    from cProfile import Profile
    from pstats import Stats, SortKey

    with Profile() as pr:
        generate_many(args)
    
    stats = Stats(pr)
    stats.sort_stats(SortKey.TIME)
    print('\n---------------\n')
    stats.print_stats()


def main():
    from sys import argv
    # ignore executable name
    args = argv[1:]

    if '-h' in args or '--help' in args:
        print('\n'.join(
            [Bcolors.f(Bcolors.OKGREEN, 'A tool for generating faded parsons problems.')
            , ''
            , 'Provide the path to well-formatted python file(s), and a question template will be generated.'
            , Bcolors.f(Bcolors.OKBLUE, 'Formatting rules:')
            , '- If the file begins with a docstring, it will become the question text'
            , '    - The question text is removed from the answer'
            , '    - Docstrings are always removed from the prompt'
            , '- Text surrounded by `?`s will become blanks in the prompt'
            , '    - Blanks cannot span more than a single line'
            , '    - The text within the question marks fills the blank in the answer'
            , '    - `?`s in any kind of string-literal or comment are ignored'
            , '- Comments are removed from the prompt *unless*'
            , '    - The comment is of the form `#{n}given` or `#blank`,' 
            , '      which are the only comments removed from the answer'
            , ''
            , Bcolors.f(Bcolors.OKBLUE, 'Flags:')
            , ' -h/--help: prints this guide'
            , ' --profile: appending anywhere in the args allows profiling this parser'
            , ' --force-json <path>: will overwrite the question\'s info.json file with auto-generated content'
            ]))
        return

    if '--profile' in args:
        args.remove('--profile')
        profile_generate_many(args)
    else:
        generate_many(args)

if __name__ == '__main__':
    main()
