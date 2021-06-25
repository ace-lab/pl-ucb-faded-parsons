/* eslint-env jquery, browser */

var ParsonsGlobal = {};

/* 
 * Initialize the widget.  Code that goes in left-hand box will be in
 * the hidden form field  named 'code-lines'. 
 * For now, no logging of events is done.
 */
ParsonsGlobal.setup = function() {
  ParsonsGlobal.widget = new ParsonsWidget({
    'sortableId': 'parsons-solution',
    'onSortableUpdate': (event, ui) => {}, // normally would log this event here.
    'trashId': 'starter-code',
    'max_wrong_lines': 1,
    'syntax_language': 'lang-py' // lang-rb and other choices also acceptable
  });
  ParsonsGlobal.widget.init($('#code-lines').val());
  ParsonsGlobal.widget.alphabetize();  // this should depend on attribute settings
}


$(document).ready(ParsonsGlobal.setup);

