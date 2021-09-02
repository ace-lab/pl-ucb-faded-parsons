from ast import *
from typing import Any

from dataclasses import dataclass

from lib.consts import Bcolors, SERVER_DEFAULT

@dataclass(init=True, repr=True, frozen=True)
class AnnotatedName:
    id: str
    annotation: str = None

class GlobalNameVisitor(NodeVisitor):
    @staticmethod
    def get_names(code: str) -> list[AnnotatedName]:
        if not code:
            return list()
        
        visitor = GlobalNameVisitor()
        visitor.visit(parse(code))
        return [AnnotatedName(n, annotation=a) for n, a in visitor.names.items()]
    
    def __init__(self) -> None:
        super().__init__()
        self.names: dict[str, str] = dict()
        self.annotation = None

    def visit_Assign(self, node: Assign) -> Any:
        for t in node.targets:
            if isinstance(t, Name) and t.id not in self.names:
                self.names[t.id] = None
    
    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        key = node.target.id
        if node.simple:
            # use unparse to stringify compound types like list[int]
            # and simple types like int
            self.names[key] = unparse(node.annotation)
        elif key not in self.names:
            self.names[key] = None
    
    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        self.names[node.name] = node.type_comment or 'python function'

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        self.names[node.name] = node.type_comment or 'python async function'

def generate_server(setup_code: str, answer_code: str, tab='    ') -> str:
    """Generates a server file by performing analysis on provided code"""
    try:
        setup_names = GlobalNameVisitor.get_names(setup_code)
    except SyntaxError as e:
        Bcolors.warn('Could not extract exports from setup: SyntaxError:', e.msg)
        setup_names = []

    try:
        answer_names = GlobalNameVisitor.get_names(answer_code)
    except SyntaxError as e:
        Bcolors.warn('Could not extract exports from answer: SyntaxError:', e.msg)
        answer_names = []

    if not setup_names and not answer_names:
        return SERVER_DEFAULT
    
    def format_annotated_name(name: AnnotatedName) -> str:
        type = name.annotation or 'python var'
        return '{"name": "' + name.id + '", "description": "", "type": "' + type + '"},'
    
    lines = \
        [ (0, '# AUTO-GENERATED FILE')
        , (0, '# go to https://prairielearn.readthedocs.io/en/latest/python-grader/#serverpy for more info')
        , (0, '')
        , (0, 'def generate(data):')
        , (1, '# Define incoming variables here')
        , (1, 'names_for_user = [')
        ]
    
    if setup_names:
        lines.extend((2, format_annotated_name(n)) for n in setup_names)
    else:
        lines.append((2, '# ex: student recieves a matrix m'))
        lines.append((2, '# {"name": "m", "description": "a 2x2 matrix", "type": "numpy array"}'))
    
    lines += \
        [ (1, ']')
        , (1, '# Define outgoing variables here')
        , (1, 'names_from_user = [')
        ]
    
    if answer_names:
        lines.extend((2, format_annotated_name(n)) for n in answer_names)
    else:
        lines.append((2, '# ex: student defines a determinant function name det'))
        lines.append((2, '# {"name": "det", "description": "determinant for a 2x2 matrix", "type": "python function"}'))
    
    lines += \
        [ (1, ']')
        , (0, '')
        , (1, 'data["params"]["names_for_user"] = names_for_user')
        , (1, 'data["params"]["names_from_user"] = names_from_user')
        , (0, '')
        , (1, 'return data')
        , (0, '')
        ]

    return '\n'.join(tab * n + t for n, t in lines)
