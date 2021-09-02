from typing import *
from os.path import *

from os import PathLike, getcwd
from dataclasses import dataclass

from lib.consts import Bcolors

def file_name(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the basename in the path without the file extensions"""
    return splitext(basename(file_path))[0]

def file_ext(file_path: PathLike[AnyStr]) -> AnyStr:
    """Returns the file extension (or '' if none exists)"""
    return splitext(basename(file_path))[1]

def write_to(parent_dir: PathLike[AnyStr], file_path: PathLike[AnyStr], data: str):
    with open(join(parent_dir, file_path), 'w+') as f:
        f.write(data)

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
    
    raise FileNotFoundError('Could not find file ' + original)


@dataclass(frozen=True, init=True)
class Arg:
    path: str
    force_json: bool = False

@dataclass(init=True)
class Args:
    args: list[Arg]
    force_json: bool = False
    quiet: bool = False
    help: bool = False
    profile: bool = False

def parse_args() -> Args:
    from sys import argv
    arg_iter = iter(argv)

    # ignore executable name
    _this_file_name = next(arg_iter)

    out = Args(list())

    for a in arg_iter:
        if a == '--profile':
            out.profile = True
        elif a == '--quiet':
            out.quiet = True
        elif a == '-h' or a == '--help':
            out.help = True
        elif a == '--force-json':
            path = next(arg_iter, default=None)
            
            if path is None:
                raise Exception('flag --force-json must be followed by a ' +
                    'path to a question source file')
            
            out.args.append(Arg(path, force_json=True))
        else: # is a path
            out.args.append(Arg(a))
    
    return out
