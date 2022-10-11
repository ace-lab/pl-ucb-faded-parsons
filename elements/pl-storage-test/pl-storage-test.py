import prairielearn as pl
import chevron
import lxml.html as xml


def render(element_html, data):
    # pl-elem-storage will not save data for 'answer's
    if data['panel'] == 'answer':
        return '<em>42</em><br>'

    html_params = { 'uuid': pl.get_uuid() }
    with open('pl-storage-test.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()
