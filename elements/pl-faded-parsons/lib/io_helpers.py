from argparse import *
from os.path import *
from typing import *

from os import getcwd, makedirs, PathLike

from lib.consts import Bcolors, PROGRAM_DESCRIPTION

def file_name(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the basename in the path without the file extensions"""
    return splitext(basename(file_path))[0]

def file_ext(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the file extension (or '' if none exists)"""
    return splitext(basename(file_path))[1]

def write_to(parent_dir: PathLike[AnyStr], file_path: PathLike[AnyStr], data: str):
    """Opens ./{parent_dir}/{file_path} and writes {data} to it"""
    with open(join(parent_dir, file_path), 'w+') as f:
        f.write(data)

def make_if_absent(dir_path: str):
    """ Creates the director(ies - nested ok) if they do not yet exist.
        Otherwise it does nothing
    """
    makedirs(dir_path, exist_ok=True)

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
        Will search ./questions/ 4th, in case this is run from <course>/
    """
    if isdir(source_path) or not file_ext(source_path):
        source_path += '.py'
    
    if exists(source_path):
        return source_path

    warn = lambda: Bcolors.warn(
        '- Could not find', original, 
        'in current directory. Proceeding with detected file.')
    
    original = source_path

    # if this is in 'elements/pl-faded-parsons', back up to course directory
    h, t0 = split(getcwd())
    _, t1 = split(h)
    if t0 == 'pl-faded-parsons' and t1 == 'elements':
        # try original in a questions directory on the course level
        new_path = join('..', '..', 'questions', original)
        if exists(new_path):
            warn()
            return new_path
        
        # try original in course directory
        new_path = join('..', '..', original)
        if exists(new_path):
            warn()
            return new_path
    
    new_path = join('questions', original)
    if exists(new_path):
        warn()
        return new_path
    
    raise FileNotFoundError('Could not find file ' + original)


def parse_args(arg_text:str = None) -> Namespace:
    """ Returns a Namespace containing all the flag and path data. 
        If arg_text is not provided, uses `sys.argv`.
    """
    parser = ArgumentParser(description=PROGRAM_DESCRIPTION, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('--profile', action='store_true', help='prints profile data after running')
    parser.add_argument('--quiet', action='store_true', help='restricts logging to warnings and errors only')
    parser.add_argument('--no-parse', action='store_true', help='prevents the code from being parsed by py.ast to derive content')

    parser.add_argument('source_path', action='append', nargs='+')
    parser.add_argument('--force-json', action='append', metavar='path', help='will overwrite the question\'s info.json file with auto-generated content')

    # if arg_text is not set, then it gets from the command line
    ns = parser.parse_intermixed_args(args=arg_text)
    
    # unpack weird nesting, delete confusing name
    ns.source_paths = [p for l in ns.source_path for p in l]
    del ns.source_path

    ns.force_json = ns.force_json or list()
    return ns
 