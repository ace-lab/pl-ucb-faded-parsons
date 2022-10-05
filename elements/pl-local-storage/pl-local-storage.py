import random
import chevron
import lxml.html as xml
import prairielearn as pl


def prepare(element_html, data):
    element = xml.fragment_fromstring(element_html)
    required = ['key']
    optional = []
    pl.check_attribs(element, required, optional)
    data['params']['key'] = pl.get_string_attrib(element, 'key', None)
    return data


def render(element_html, data):
    html_params = {
        'key': data['params']['key']
    }
    with open('pl-local-storage.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()
