/* eslint-env jquery, browser */

var ParsonsGlobal = {
  indentWidth: 4
};

/*
 * Grab the lines in the appropriate box and stuff them into hidden HTML elements for 
 * form submission.  We need to retrieve these by calling the Parsons JS widget, because
 * the HTML/CSS info doesn't tell us the indentation level of each line :-(
 */

ParsonsGlobal.grabListAndStuffInto = function(fromSelector, toSelector) {
  var grabOneLine = function(lineObj) {
    return(" ".repeat(lineObj.indent * ParsonsGlobal.indentWidth) + lineObj.code);
  };
  var theLines = ParsonsGlobal.widget.getModifiedCode('#ul-' + fromSelector);
  var theCode = $.map(theLines, grabOneLine);
  // put the whole newline-separated list into toSelector
  $(toSelector).val(theCode.join("\n"));

};
          
/*
 * When form is submitted, capture the state of the student's work in both boxes
 * by populating the hidden form fields, which will be submitted.
 */
ParsonsGlobal.submitHandler = function() {
  ParsonsGlobal.grabListAndStuffInto('starter-code', '#student-starter-code');
  ParsonsGlobal.grabListAndStuffInto('parsons-solution', '#student-parsons-solution');
}

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
  // when form submitted, grab the student work and put it into hidden form fields
  $('form.question-form').submit(ParsonsGlobal.submitHandler);
};



$(document).ready(ParsonsGlobal.setup);

