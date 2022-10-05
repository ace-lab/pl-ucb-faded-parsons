## Adapted from the PrairieLearn/elements/pl-rich-text-editor/pl-rich-text-editor.py source ##

import prairielearn as pl
import lxml.html
import chevron
import base64
import hashlib

def get_answer_name(file_name):
    return '_local_storage_{0}'.format(hashlib.sha1(file_name.encode('utf-8')).hexdigest())


def element_inner_html(element):
    return (element.text or '') + ''.join(str(lxml.html.tostring(c), 'utf-8') for c in element.iterchildren())


def add_format_error(data, error_string):
    if '_files' not in data['format_errors']:
        data['format_errors']['_files'] = []
    data['format_errors']['_files'].append(error_string)


def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ['filename']
    optional_attribs = []
    pl.check_attribs(element, required_attribs, optional_attribs)

    file_name = pl.get_string_attrib(element, 'filename')
    if '_required_file_names' not in data['params']:
        data['params']['_required_file_names'] = []
    elif file_name in data['params']['_required_file_names']:
        raise Exception('There is more than one file editor with the same file name.')
    data['params']['_required_file_names'].append(file_name)


def render(element_html, data):
    if data['panel'] == 'answer':
        return ''

    if not (data['panel'] == 'question' or data['panel'] == 'submission'):
        raise Exception('Invalid panel type: ' + data['panel'])

    element = lxml.html.fragment_fromstring(element_html)
    file_name = pl.get_string_attrib(element, 'key', '')
    answer_name = get_answer_name(file_name)
    uuid = pl.get_uuid()
    element_text = element_inner_html(element)

    html_params = {
        'name': answer_name,
        'uuid': uuid
    }

    if data['panel'] != 'question':
        html_params['container_class'] = 'plls-readonly'

    if element_text is not None:
        text_display = str(element_text)
    else:
        text_display = ''

    html_params['original_file_contents'] = base64.b64encode(text_display.encode('UTF-8').strip()).decode()

    submitted_file_contents = data['submitted_answers'].get(answer_name, None)
    if submitted_file_contents:
        html_params['current_file_contents'] = submitted_file_contents
    else:
        html_params['current_file_contents'] = html_params['original_file_contents']

    with open('pl-local-storage.mustache', 'r', encoding='utf-8') as f:
        return chevron.render(f, html_params).strip()


def parse(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    file_name = pl.get_string_attrib(element, 'key', '')
    answer_name = get_answer_name(file_name)

    # Get submitted answer or return parse_error if it does not exist
    file_contents = data['submitted_answers'].get(answer_name, None)
    if not file_contents:
        add_format_error(data, 'No submitted answer for {0}'.format(file_name))
        return

    submitted_files = data['submitted_answers'].get('_files', None)
    if submitted_files is None:
        data['submitted_answers']['_files'] = []
    elif not isinstance(submitted_files, list):
        add_format_error(data, '_files was present but was not an array.')
        return

    data['submitted_answers']['_files'].append({
        'name': file_name,
        'contents': file_contents
    })
