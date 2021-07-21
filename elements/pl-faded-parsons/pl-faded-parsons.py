from contextlib import redirect_stdout
from io import StringIO
import lxml
import prairielearn as pl
import lxml.html as xml
import random
import chevron
import os
import json
import math

WEIGHT_DEFAULT = 1
BASE_DEFAULT = 10

QUESTION_CODE_FILE     = 'code_lines.py'
SOLUTION_CODE_FILE    = 'solution.py'
SOLUTION_NOTES_FILE   = 'solution_notes.md'
TEST_CASES_FILE       = 'testcases.json'

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

def read_json_file(data, filename, error_if_not_found=True):
    """Return dictionary from some JSON in serverFilesQuestion."""
    path = os.path.join(data["options"]["question_path"], 'serverFilesQuestion', filename)
    try:
        f = open(path, 'r')
        return json.load(f)
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

def get_output(code):
    f = StringIO()
    with redirect_stdout(f):
        try:
            exec(code)
        except Exception as e:
            return f'Error: {e}'
    return f.getvalue().strip()

def render_question_panel(element_html, data):
    """Render the panel that displays the question (from code_lines.py) and interaction boxes"""
    html_params = {
        "code_lines":  read_file_lines(data, QUESTION_CODE_FILE),
    }
    with open('pl-faded-parsons-question.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()

def render_submission_panel(element_html, data):
    """Show student what they submitted"""
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, 'answers-name')
    partial_score = data['partial_scores'].get(name, {'score': None})
    score = partial_score.get('score', None)
    html_params = {
        'submission': True,
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
    lang = pl.get_string_attrib(element, 'language')

    # TBD do error checking here for other attribute values....
    # set data['format_errors']['elt'] to an error message indicating an error with the
    # contents/format of the HTML element named 'elt'

    return

def grade(element_html, data):
    """Grade the student's response; many strategies are possible..."""
    student_code = get_student_code(element_html, data)

    # at this point `student_code` is a string representing the exact submitted Python code
    # at a minimum, we have to set data['score'] to a value from 0.0...1.0
    # test_cases = read_json_file(data, TEST_CASES_FILE)

    # # run test cases
    # correct_answers = []
    # student_answers = []
    # correct, wrong = 0, 0
    # for index, test_case in enumerate(test_cases, 1):
    #     test = test_case[f'case_{index}']
    #     correct_answer = test_case[f'answer_{index}']
    #     code_to_run = student_code + f'\nprint({test})'
    #     student_answer = get_output(code_to_run)
    #     correct_answers.append(correct_answer)
    #     student_answers.append(student_answer)
    #     if student_answer == correct_answer:
    #         correct += 1
    #     else:
    #         wrong += 1

    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, 'answers-name')

    # Get weight
    weight = pl.get_integer_attrib(element, 'weight', WEIGHT_DEFAULT)
    # for index in range(len(test_cases)):
        # test = test_cases[index]
        # correct_answer = answers[index]
        # code_to_run = student_code + f'\nprint({test})'
        # student_answer = get_output(code_to_run)
        # correct_answers.append(correct_answer)
        # student_answers.append(student_answer)
        # if student_answer == correct_answer:
        #     correct += 1
        # else:
        #     wrong += 1
    # data['correct_answers'] = correct_answers
    # data['submitted_answers'] = student_answers
    # data['score'] = (correct/(correct+wrong))
    data['partial_scores'][name] = {'score': 0.3, 'weight': weight}