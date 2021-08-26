from typing import *
import re

""" Matches, with precedence in listed order:
    - capture group 0
        - (one-line) comments (including the line-break terminator)
    - capture group 1
        - (one-line) single-apostrophe string literals
        - (multi-line) triple-quote string literals
        - (one-line) single-quote string literals
    - capture group 2
        - (one-line) answer surrounded by ?'s (excluding the ?'s)
"""
PATTERN = re.compile(r'(\#.*?\r?\n)|(\'.*?\'|\"\"\"[\s\S]*?\"\"\"|\".*?\")|\?(.*?)\?')

BLANK_SUBSTITUTE = "!BLANK"

def extract_prompt_ans(source_code: str, keep_comments_in_prompt: bool = False) -> Tuple[str, str]:
    """ Extracts from one well-formatted `source_code` string the text for both
        the starting prompt and the answer text. Formatting rules:
            - Text that will be represented as blanks must be surrounded by `?`
            - Blanks cannot span more than a single line
            - `?`s in any kind of string-literal or comment are ignored
        
        Note: Empty lines are always stripped from the prompt. Comments are
        also removed by default, but setting `keep_comments_in_prompt` to True 
        will keep them in.
            
        e.g.
        ```
        > source = "sum = lambda a, b: ?a + b?"
        > extract_prompt_ans(source)
        ("sum = lambda a, b: !BLANK", "sum = lambda a, b: a + b")

        > source = "?del bad?  # What's going on?!?"
        > extract_prompt_ans(source)
        ("!BLANK", "del bad  # What's going on?!?!")
        ```"""
    prompt_code = ''
    answer_code = ''

    # (exclusive) end of the last match
    last_end = 0

    for match in re.finditer(PATTERN, source_code):
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
            # add comment to answer code, and maybe prompt_code
            answer_code += comment
            
            # even if excluding the comment from the prompt,
            # every comment ends with a '\n'.
            # must keep it to maintain whitespacing
            prompt_code += comment if keep_comments_in_prompt else '\n'
        elif string:
            # strings always stay in both
            prompt_code += string
            answer_code += string
        elif blank_ans:
            # fill in proper blank text
            prompt_code += BLANK_SUBSTITUTE
            answer_code += blank_ans

    # don't forget everything after the last match!
    unmatched = source_code[last_end:]
    prompt_code += unmatched
    answer_code += unmatched
    
    # remove all whitespace-only lines 
    # usually as a result of removing comments)
    # then remove all indentation
    prompt_code = '\n'.join(filter(bool, map(str.strip, prompt_code.splitlines())))

    return prompt_code, answer_code

if __name__ == '__main__':
    with open('master.py', 'r') as source:
        source_code = ''.join(source)
        prompt_code, answer_code = extract_prompt_ans(source_code)
        print(prompt_code, answer_code, sep="\n\n --- \n\n")
        
