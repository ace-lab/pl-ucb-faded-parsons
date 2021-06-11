/* eslint-env jquery, browser */

/* files in here may assume that jQuery is loaded */
/* (question: at what point does THIS file get loaded??) */

$(function() {
  $('.example-course-custom-element').append('<p>This text was added by a script.</p>');
})
