/* eslint-env jquery, browser */

var ParsonsGlobal = {};

/*
 * Grab the lines in the starter-code box and student-solution box 
 * and stuff them into hidden HTML elements for form submission.
 */

ParsonsGlobal.grabListAndStuffInto = function(fromSelectors, toSelector) {
  $(toSelector + ' li').val(
    $(fromSelectors).
      map(function() { return $(this).text(); }).
      get().
      join("\n"));
};
          
/*
 * When form is submitted, capture the state of the student's work in both boxes
 * by populating the hidden form fields, which will be submitted.
 */
ParsonsGlobal.submitHandler = function() {
  ParsonsGlobal.grabListAndStuffInto('#starter-code', '#student-starter-code');
  ParsonsGlobal.grabListAndStuffInto('#parsons-solution', '#student-starter-code');
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

