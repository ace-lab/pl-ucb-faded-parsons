import prairielearn as pl
import lxml.html as xml
import random
import chevron


def prepare(element_html, data):
    data['params']['random_number'] = random.random()
    return data


def render(element_html, data):
    html_params = {
        'number': data['params']['random_number'],
        'image_url': data['options']['client_files_element_url'] + '/block_i.png'
    }
    with open('course-element.mustache', 'r') as f:
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

    # only Python examples allowed right now (lang MUST be "py")
    lang = pl.get_string_attrib(element, 'language')

    # TBD do error checking here for other attribute values....

    return

def grade(element_html, data):
    element = xml.fragment_fromstring(element_html)
    data['score'] = 1.0
    return data

    
