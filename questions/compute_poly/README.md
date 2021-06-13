# Faded Parsons example

The `clientFilesQuestion/compute_poly.yaml` file is the original representation used by the
standalone FPP tool...in a normal FPP question (once this element is
implemented), this file should never be needed.

The problem prompt (`problem_description` key in the file) just goes
into a `pl-question-panel` element in `question.html`.

For the rest of the keyes, `clientFilesQuestion` should contain the
following, where each base filename represents the corresponding key
in the Yaml file:

* `initial_code.py` - the code initially given as part of solution 

* `code_lines.py` - the code that will be scrambled and shown to
student, including `!BLANK` wherever a blank should occur  (so
technically these lines are not valid Python).  Order doesn't matter,
as the lines will be arranged by the UI according to the `order`
attribute of the `pl-faded-parsons` element


* `solution.py` - This is what's shown to students on the solution
page for the problem.  See `question.html` for how this is rendered in
the answer panel using existing PL elements.

The following are used for testing/autograding:

* `test.py` - test case(s) run when the student submits the question
for grading (ie to get their own feedback).  This file subsumes the
`test_fn` and `test_cases` keys in the Yaml file and substitutes a
single entry point called `test()` that runs the test case(s) in
turn.  **TBD we have to talk about how the grader generates output.
If we use the existing PL external Python grader (would be nice if it
just worked), it must generate its results in [this
format](https://prairielearn.readthedocs.io/en/latest/externalGrading/#grading-result). 

* `hidden_test.py` - test case(s) run only on "final" submission and
not visible to students (optional).
**NOTE:** We need to talk through how this would work in
PL; maybe these are only used when the assessment is in summative vs
formative?.  Perhaps initially we just have `test.py` until we figure
this out.

