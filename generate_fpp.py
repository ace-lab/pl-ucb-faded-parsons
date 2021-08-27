from typing import *
import re
from sys import argv
from os import makedirs, path, PathLike
from shutil import copyfile

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
    with open(source_path, 'r') as source:
        source_code = ''.join(source)
        prompt_code, answer_code = extract_prompt_ans(source_code)
    
    question_name = filename(source_path)

    test_dir = path.join(question_name, 'tests')
    makedirs(test_dir, exist_ok=True)

    copyfile(source_path, path.join(question_name, 'source.py'))
    
    with open(path.join(test_dir, 'ans.py'), 'w+') as f:
        f.write(answer_code)
    
    with open(path.join(question_name, 'question.html'), 'w+') as f:
        question_html = generate_question_html(prompt_code)
        f.write(question_html)
    
    with open(path.join(question_name, 'info.json'), 'w+') as f:
        f.write('{}\n')


if __name__ == '__main__':
    if len(argv) < 2:
        raise Exception('Please provide a source code path as a first CLI argument')
    
    source_path = argv[1]

    print('Generating from source', source_path, '...')    

    generate_fpp_question(source_path)

    print('Done.')


        
