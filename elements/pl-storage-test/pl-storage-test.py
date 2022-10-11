import prairielearn as pl
import chevron
import lxml.html as xml


def render(element_html, data):
    if data['panel'] == 'answer':
        return '<em>42</em><br>'

    html_params = {
        'uuid': pl.get_uuid(),
        'original_contents': element_html
    }
    with open('pl-storage-test.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()
