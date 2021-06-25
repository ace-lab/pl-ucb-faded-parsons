import prairielearn as pl
import lxml.html as xml
import random
import chevron
import os

HTML_MUSTACHE_TEMPLATE = 'pl-faded-parsons.mustache'
QUESTION_CODE_FILE     = 'code_lines.py'
SOLUTION_CODE_FILE    = 'solution.py'

# HTML element names must match pl-faded-parsons.mustache:

STUDENT_SOLUTION_ELT   = 'student-parsons-solution'
UNUSED_LINES_ELT       = 'student-starter-code'


def prepare(element_html, data):
    data['params']['random_number'] = random.random()
    return data

def render_question_panel(element_html, data):
    """Render the panel that displays the question (from code_lines.py) and interaction boxes"""
    html_params = {}
    html_params["code_lines"] = read_code_lines(data, QUESTION_CODE_FILE)
    with open(HTML_MUSTACHE_TEMPLATE, 'r') as f:
        return chevron.render(f, html_params).strip()

def render_submission_panel(element_html, data):
    html_params = {}
    pass


def render_answer_panel(element_html, data):
    """Render the contents of the panel showing the instructor's reference solution"""
    html_params = {}
    pass

def render(element_html, data):
    panel_type = data['panel']
    if panel_type == 'question':
        return render_question_panel(element_html, data)
    elif panel_type == 'submission':
        return render_submission_panel(element_html, data)
    elif panel_type == 'answer':
        return render_answer_panel(element_html, data)
    else:
        raise Exception(f'Invalid panel type: {panel_type}')



def parse(element_html, data):
    """Parse student's submitted answer (HTML form submission)"""
    # make an XML fragment that can be passed around to other PL functions,
    # parsed/walked, etc
    element = xml.fragment_fromstring(element_html)

    # `element` is now an XML data structure - see docs for LXML library at lxml.de
    
    # only Python problems are allowed right now (lang MUST be "py")
    lang = pl.get_string_attrib(element, 'language')

    # TBD do error checking here for other attribute values....
    # set data['format_errors']['elt'] to an error message indicating an error with the
    # contents/format of the HTML element named 'elt'                               

    return

def grade(element_html, data):
    element = xml.fragment_fromstring(element_html)
    data['score'] = 1.0

    student_code = data['submitted_answers'].get(STUDENT_SOLUTION_ELT, None)
    raise Exception(f'Student starter code:\n{student_code}')


    
#
# Helper functions
#
def read_code_lines(data, filename):
    """Return a string of newline-separated lines of code from some file in serverFilesQuestion."""
    path = os.path.join(data["options"]["question_path"], 'serverFilesQuestion', filename)
    f = open(path, 'r')
    return f.read()