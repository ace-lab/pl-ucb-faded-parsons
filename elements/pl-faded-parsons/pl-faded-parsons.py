import code
import prairielearn as pl
import lxml.html as xml
import random
import chevron
import os
import pygments
import html

QUESTION_CODE_FILE     = 'code_lines.py'
SOLUTION_CODE_FILE    = 'solution.py'
SOLUTION_NOTES_FILE   = 'solution_notes.md'

def prepare(element_html, data):
    data['params']['random_number'] = random.random()
    return data

    
#
# Helper functions
#
def read_file_lines(data, filename, error_if_not_found=True):
    """Return a string of newline-separated lines of code from some file in serverFilesQuestion."""
    path = os.path.join(data["options"]["question_path"], 'serverFilesQuestion', filename)
    try:
        f = open(path, 'r')
        return f.read()
    except FileNotFoundError as e:
        if error_if_not_found:
            raise e
        else:
            return False

def get_answers_name(element_html):
    # use answers-name to namespace multiple pl-faded-parsons elements on a page
    element = xml.fragment_fromstring(element_html)
    answers_name = pl.get_string_attrib(element, 'answers-name', None)
    if answers_name is not None:
        answers_name = answers_name + '-'
    else:
        answers_name = ''
    return answers_name

def get_student_code(element_html, data):
    element = xml.fragment_fromstring(element_html)
    answers_name = get_answers_name(element_html)
    student_code = data['submitted_answers'].get(answers_name + 'student-parsons-solution', None)
    return student_code


def render_question_panel(element_html, data):
    """Render the panel that displays the question (from code_lines.py) and interaction boxes"""

    element = xml.fragment_fromstring(element_html)
    answers_name = get_answers_name(element_html)
    vertical_format = pl.get_string_attrib(element, "format", "") == "vertical"

    html_params = {
        "answers_name": answers_name,
    }

    def get_child_text_by_tag(element, tag: str) -> str:
        """get the innerHTML of the first child of `element` that has the tag `tag`
        default value is empty string"""
        return next( 
            (   elem.text 
                for elem in element 
                if elem.tag == tag  ), 
            ""
        )
    
    code_lines = get_child_text_by_tag(element, "code-lines")

    if vertical_format: 
        
        pre_text = get_child_text_by_tag(element, "pre-text")
        post_text = get_child_text_by_tag(element, "post-text")

        lang = pl.get_string_attrib(element, "language", None)

        while pre_text[-1] == "\n":
            pre_text = pre_text[:-1]
        while post_text[0] == '\n':
            post_text = post_text[1:]
            
        html_params.update({
            "vertical" : {
                "pre_text" : pre_text,
                "post_text" : post_text,
                "answers_name" : answers_name,
            },
        })

        if lang is not None:
            html_params["vertical"].update({
                "language" : f"language=\"lang\""
            })
    
    if code_lines == "":
        html_params.update({ 
            "code_lines" : read_file_lines(data, QUESTION_CODE_FILE) 
        })
    else:
        html_params.update({
            "code_lines" : code_lines
        })

    with open('pl-faded-parsons-question.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()

def render_submission_panel(element_html, data):
    """Show student what they submitted"""
    html_params = {
        "code" : get_student_code(element_html, data),
    }
    with open('pl-faded-parsons-submission.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()


def render_answer_panel(element_html, data):
    """Show the instructor's reference solution"""
    html_params = {
        "notes": read_file_lines(data, SOLUTION_NOTES_FILE, error_if_not_found=False)
    }
    with open('pl-faded-parsons-answer.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()

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
    # lang = pl.get_string_attrib(element, 'language') # TODO: commenting is a stop gap for the pilot study, find a better solution

    # TBD do error checking here for other attribute values....
    # set data['format_errors']['elt'] to an error message indicating an error with the
    # contents/format of the HTML element named 'elt'                               

    return

def grade(element_html, data):
    """Grade the student's response; many strategies are possible..."""
    student_code = get_student_code(element_html, data)
    # at this point `student_code` is a string representing the exact submitted Python code
    # at a minimum, we have to set data['score'] to a value from 0.0...1.0 
    data['score'] = 1.0
    return(data)

