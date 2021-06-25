import prairielearn as pl
import lxml.html as xml
import random
import chevron
import os


def prepare(element_html, data):
    data['params']['random_number'] = random.random()
    return data


def render(element_html, data):
    html_params = {}
    # read all the lines of serverFilesCourse/code_lines.py into an array
    html_params["code_lines"] = read_code_lines(data)
    with open('pl-faded-parsons.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()

#
# Called to parse student's submitted answer (HTML form submission)
# set data['format_errors']['elt'] to an error message indicating an error with the
# contents/format of the HTML element named 'elt'
#

def parse(element_html, data):
    # make an XML fragment that can be passed around to other PL functions,
    # parsed/walked, etc
    element = xml.fragment_fromstring(element_html)

    # `element` is now an XML data structure - see docs for LXML library at lxml.de
    
    # only Python problems are allowed right now (lang MUST be "py")
    lang = pl.get_string_attrib(element, 'language')

    # TBD do error checking here for other attribute values....

    return

def grade(element_html, data):
    element = xml.fragment_fromstring(element_html)
    data['score'] = 1.0
    raise Exception("Student starter code:\n" + data['raw_submitted_answers']['student-parsons-solution'])


    
#
# Helper functions
#
def read_code_lines(data):
    path = os.path.join(data["options"]["question_path"], 'serverFilesQuestion', 'code_lines.py')
    f = open(path, 'r')
    return f.read()
