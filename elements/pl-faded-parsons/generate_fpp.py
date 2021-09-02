from typing import *

from collections import defaultdict
from json import dumps
from os import getcwd, makedirs, path, PathLike
from re import finditer, match as test
from shutil import copyfile
from uuid import uuid4

from lib.consts import *
from lib.name_visitor import *

def extract_regions(source_code: str, keep_comments_in_prompt: bool = False) -> Dict[str, str]:
    """ Extracts from well-formatted `source_code` string the text for the question, 
        the problem starting code, the answer code, and any other custom regions

        Formatting rules:
        - If the file begins with a docstring, it will become the `question_text` region
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
        - Custom regions are begun and ended by `## {region name} ##`
            - A maximum of one region may be open at a time
            - All text in a region is only copied into that region
            - Regions must be closed before the end of the source string
        
            
        e.g.
        ```
        > source = "sum = lambda a, b: ?a + b? #0given"
        > extract_regions(source)
        {'prompt_code': "sum = lambda a, b: !BLANK #0given", 'answer_code': "sum = lambda a, b: a + b"}

        > source = "\\\"\\\"\\\"Make good?\\\"\\\"\\\" ?del bad?  # badness?!?"
        > extract_regions(source)
        {'question_text': "Make good?", 'prompt_code': "!BLANK", 'answer_code': "del bad  # badness?!?!"}
        ```
    """
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
                regions['question_text'] = docstring[3:-3]
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

    regions['prompt_code'] = prompt_code
    regions['answer_code'] = answer_code

    return regions

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

def file_name(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the basename in the path without the file extensions"""
    return path.splitext(path.basename(file_path))[0]

def file_ext(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the file extension (or '' if none exists)"""
    return path.splitext(path.basename(file_path))[1]

def write_to(parent_dir: PathLike[AnyStr], file_path: PathLike[AnyStr], data: str):
    with open(path.join(parent_dir, file_path), 'w+') as f:
        f.write(data)

def generate_fpp_question(
    source_path: PathLike[AnyStr], 
    force_generate_json: bool = False,
    log_details=True):
    """ Takes a path of a well-formatted source (see `extract_prompt_ans`),
        then generates and populates a question directory of the same name.
    """
    Bcolors.printf(Bcolors.OKBLUE, 'Generating from source', source_path)

    if log_details:
        print('- Extracting from source...')
    
    with open(source_path, 'r') as source:
        source_code = ''.join(source)
        regions = extract_regions(source_code)
    
    def remove_region(key, default=''):
        if key in regions:
            v = regions[key]
            del regions[key]
            return v
        return default

    question_name = file_name(source_path)

    # create all new content in a new folder that is a
    # sibling of the source file in the filesystem
    question_dir = path.join(path.dirname(source_path), question_name)

    if log_details:
        print('- Creating destination directories...')
    
    test_dir = path.join(question_dir, 'tests')
    makedirs(test_dir, exist_ok=True)

    copy_dest_path = path.join(question_dir, 'source.py')
    if log_details:
        print('- Copying {} to {} ...'.format(path.basename(source_path), copy_dest_path))
    copyfile(source_path, copy_dest_path)

    if log_details:
        print('- Populating {} ...'.format(question_dir))
    
    prompt_code = remove_region('prompt_code')
    question_text = remove_region('question_text')
    question_html = generate_question_html(prompt_code, question_text=question_text)
    write_to(question_dir, 'question.html', question_html)
    
    json_path = path.join(question_dir, 'info.json')
    json_region = remove_region('info.json')
    missing_json = not path.exists(json_path)
    if force_generate_json or json_region or missing_json:
        json_text = json_region or generate_info_json(question_name)
        write_to(question_dir, 'info.json', json_text)
        if not missing_json:
            Bcolors.warn('  - Overwriting', json_path, 
                'using \"info.json\" region...' if json_region else '...')

    setup_code = remove_region('setup_code', SETUP_CODE_DEFAULT)
    answer_code = remove_region('answer_code')

    write_to(question_dir, 'server.py', remove_region('server') or generate_server(setup_code, answer_code))

    if log_details:
        print('- Populating {} ...'.format(test_dir))

    write_to(test_dir, 'ans.py', answer_code)
    
    write_to(test_dir, 'setup_code.py', setup_code)

    write_to(test_dir, 'test.py', remove_region('test', TEST_DEFAULT))

    if regions:
        Bcolors.warn('- Writing unrecognized regions:')
    
    for raw_path, data in regions.items():
        if not raw_path:
            Bcolors.warn('  - Skipping anonymous region!')
            continue

        # if no file extension is given, give it .py
        if not file_ext(raw_path):
            raw_path += '.py'
        
        # ensure that the directories exist before writing
        final_path = path.join(question_dir, raw_path)
        makedirs(path.dirname(final_path), exist_ok=True)
        Bcolors.warn('  -', final_path, '...')

        # write files
        write_to(question_dir, raw_path, data)

    Bcolors.printf(Bcolors.OKGREEN, 'Done.')

def resolve_source_path(source_path: str) -> str:
    """ Attempts to find a matching source path in the following destinations:

        ```
        standard course directory structure:
        + <course>  
        | ...        << search here 3rd
        |-+ elements/pl-faded-parsons
        | |-generate_fpp.py
        | | ...      << search here 1st
        |
        |-+ questions
        | | ...      << search here 2nd
        |
        ```
    """
    if path.isdir(source_path) or not file_ext(source_path):
        source_path += '.py'
    
    if path.exists(source_path):
        return source_path

    warn = lambda: Bcolors.warn(
        '- Could not find', original, 
        'in current directory. Proceeding with detected file. -')
    
    original = source_path

    # if this is in 'elements/pl-faded-parsons', back up to course directory
    h, t0 = path.split(getcwd())
    _, t1 = path.split(h)
    if t0 == 'pl-faded-parsons' and t1 == 'elements':
        # try original in a questions directory on the course level
        new_path = path.join('..', '..', 'questions', original)
        if path.exists(new_path):
            warn()
            return new_path
        
        # try original in course directory
        new_path = path.join('..', '..', original)
        if path.exists(new_path):
            warn()
            return new_path
    
    raise FileNotFoundError('Could not find file ' + original)

def generate_many(args: list[str]):
    if not args:
        raise Exception('Please provide at least one source code path as an argument')

    force_json = False
    successes, failures = 0, 0
    for source_path in args:
        if source_path.startswith('--'):
            if source_path.endswith('force-json'):
                force_json = True
            else:
                Bcolors.warn('-', source_path, 
                    'not recognized as a flag! use --help for more info. -')
            continue

        try:
            source_path = resolve_source_path(source_path)
            generate_fpp_question(source_path, force_generate_json=force_json)
            successes += 1
        except SyntaxError as e:
            Bcolors.fail('SyntaxError:', e.msg, 'in', source_path)
            failures += 1
        except FileNotFoundError:
            Bcolors.fail('FileNotFoundError:', source_path)
            failures += 1

        force_json = False
    
    # print batch feedback
    if successes + failures > 1:
        n_files = lambda n: str(n) + ' file' + ('' if n == 1 else 's')
        if successes:
            Bcolors.printf(Bcolors.OKGREEN, 'Batch completed successfullly on', n_files(successes), end='')
            if failures:
                Bcolors.fail(' and failed on', n_files(failures))
            else:
                print()
        else:
            Bcolors.fail('Batch failed on all', n_files(failures))

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
            [ Bcolors.f(Bcolors.OKGREEN, 'A tool for generating faded parsons problems.')
            , ''
            , 'Provide the path to well-formatted python file(s), and a question template will be generated.'
            , 'This tool will search for a path in ./ ../../questions/ and ../../ before erring'
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
            , '- Custom regions are begun and ended by `## {region name} ##`'
            , '    - A maximum of one region may be open at a time'
            , '    - All text in a region is only copied into that region'
            , '    - Regions must be closed before the end of the source string'
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
