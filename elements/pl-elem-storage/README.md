PrairieLearn Element Storage
=====

The `pl-elem-storage` element provides easy storage between page reloads for
other custom PrairieLearn elements.

Example
----
Say you were making an new element called `custom-element` that contained a
textbox for short answer:
``` html
<!-- inside custom-element.mustache -->
<textarea name="custom-element-text-editor"></textarea>
```
``` python
# inside custom-element.py
def render(element_html, data):
    html_params = {}
    # any other params are set...
    with open('custom-element.mustache', 'r') as f:
        return chevron.render(f, html_params)
```

The default behavior of PrairieLearn is to lose the contents of that textbox
between reloads, e.g. for a "Save & Grade" request.
Note that when you hit "Save & Grade," PrairieLearn creates a page with *two*
instances of `custom-element` rendered: one to edit and resubmit in the usual
question box, and another to view the previously submitted answer.
In PrairieLearn's terms, these are the "question" and "submission" panels,
respectively.
(Depending on the settings for the question your element is used in there may
be a third instance rendered to show the instructor provided solution, i.e the
"answer" panel.)
Each of these panels will have a potentially different value of text, and it is
important that we track each instance's values separately.

In order to avoid losing the student's data, we add an `pl-elem-storage`
element.
The element requires a uuid to be generated on each **render** call, so that
each rendered instance of the element will be tied to exactly one store of
data.
To identify the textarea, we add an id attribute that includes this uuid.
Finally we add a script that contains the logic for when to update the
data in the textarea.
``` html
<!-- inside custom-element.mustache -->
<textarea
    name="custom-element-text-editor"
    id="custom-element-text-editor-{{uuid}}"></textarea>

<pl-elem-storage
    filename="custom-element-storage"
    uuid="{{uuid}}"></pl-elem-storage>

<script>
    $(function() {
        // retrieve the registered store
        const store = PlElemStorage.getStore('{{uuid}}');

        // populate the textbox with the old data
        const editor = $('#custom-element-text-editor-{{uuid}}');
        editor.val(store());

        // set a listener for edits in the textbox
        editor.on('input', function() { store(editor.val()); });
    });
</script>
```

To add the uuid data, we edit the `custom-element.py` file to include a uuid
when chevron renders our mustache file:
``` python
# inside custom-element.py
import prairielearn as pl  # always available in the pl docker image

def render(element_html, data):
    html_params = {}
    # any other params are set...
    html_params['uuid'] = pl.get_uuid()
    with open('custom-element.mustache', 'r') as f:
        return chevron.render(f, html_params)
```
