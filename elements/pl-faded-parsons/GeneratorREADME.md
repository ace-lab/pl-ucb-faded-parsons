# On Generating Questions

## Setup

### Development Requirements

- Docker

Via docker, the appropriate images can be maintained and installed. 
You may optionally install [a local prairielearn clone](https://github.com/PrairieLearn/PrairieLearn) if you want to tinker with its internals.


### PrairieLearn Directory Structure

Your codebase should be structured like this:
```
root-course-directory
|   ...
|
+-- elements
|   +-- pl-faded-parsons        << contains all required FPP files
|   |   generate_fpp.py         << the main script for content generation
|   |   ...
|
+-- questions                   << auto-detect targets the questions directory
|   |   question1.py            <<
|   |   question2.py            << the source files for generating...
|   |   ...                     <<
|   |
|   +-- question1               <<
|   +-- question2               << ...these prairielearn questions
|   |   ...                     <<
```

To begin writing any FPP questions, you will need the `pl-faded-parsons` directory and all of its contents. 
It contains all the html and js files required by prairielearn to display a `<pl-faded-parsons>` element.

This element is then used by questions you would traditionally write as subfolders in the `questions` directory. 
The tool `generate_fpp.py` will take well-formatted python files and turn them into a question folder.

### Grading

The tool has the ability to generate testing content, but the prairielearn's python autograder will not be able to be run locally without following [these steps in the pl dev guide](https://prairielearn.readthedocs.io/en/latest/externalGrading/#running-locally-for-development) to initialize docker correctly.

## Formatting a Source File

### Usable Files

Any file following the semantic rules (see below) may be provided, but the tool will only autodetect python files.

This tool will search for a provided path in `./`, `questions/`, `../../questions/`, and finally `../../` before erring.
If none is provided, it will hunt for a `questions` directory in these locations, and use all .py files there.
 
### Semantic Rules
 - If the file begins with a docstring, it will become the question text
     - The question text is removed from the answer
     - Docstrings are always removed from the prompt
 - Text surrounded by `?`s will become blanks in the prompt
     - Blanks cannot span more than a single line
     - The text within the question marks fills the blank in the answer
     - `?`s in any kind of string-literal or comment are ignored
 - Comments are removed from the prompt unless the comment matches a special form: 
     - `#{n}given`: include as a part of the start solution (n-times-indented)
     - `#blank {txt}`: use txt as the default for a blank in the preceding line
     - These special forms are the only comments removed from the answer
 - Regions are begun and ended by `## {region name} ##`
     - A maximum of one region may be open at a time
     - Regions must be closed before the end of the source
     - All text in a region is only copied into that region
     - Text will be copied into a new file with the regions name in the
       question directory, excluding these special regions:
         - explicit: `test` `setup_code`
         - implicit: `answer_code` `prompt_code` `question_text`
     - Code in `setup_code` will be parsed to extract exposed names unless the --no-parse
       flag is set. 
         - Type annotations and function docstrings are used to fill out server.py and the Provided section of the prompt text
     - Any custom region that clashes with an automatically generated file name
       will overwrite the automatically generated code
 - Import regions allow for the contents of arbitrary files to be loaded as regions
     - They are formatted as `## import {rel_file_path} as {region name} ##`
        where `rel_file_path` is the relative path to the file from the source file
     - Like regular regions, they cannot be used inside of another region

### An Example Source File

Before running the tool, the questions directory takes the form
```
questions
|   sublist.py
```

At the header of `sublist.py` we have a docstring which will become the prompt.
``` python
""" Make a function <code>is_sublist</code> that checks whether the first
    argument contains the second as a sublist (including ordering), eg

    <pl-code language="python">
    >> is_sublist(['a', 'b', 'c', 'd'], ['b', 'c'])
    True
    >> is_sublist([1, 2, 3, 4], [4, 3])
    False</pl-code>
"""
...
```

Then we have the solution with blanks.
``` python
...
def is_sublist(lst, sublist): #0given
    n, m = len(lst), len(sublist) #1given
    # we only want to search to the last place
    # where the sublist could occur (n - m - 1)
    for i in range(?n - m?):
        start, end = i, i + m
        # compare to the slice of len m at i
        if lst[?start:end?] == sublist: #blank _:_
            return ?True? # return early!
    return False #1given
...
```

Note that the full line comments as well as the `# return early!` comments will be included in the reference solution, but not the sortable code lines.

By contrast, the special-form comments (eg `#0given` and `#blank _:_`) will not appear in the reference solution, but will edit the starting configuration of the sortable code lines.
(`#0given` includes `def is_sublist(lst, sublist):` as a part of the starting solution with 0 indents, `#1given` includes `return False` with 1 indent, and `#blank _:_` sets the inital text of the blank in the brackets to `_:_`. )

Note there is no way to indicate a red-herring or distractor line! 
Distractors are philosophically  antithetical to the design of FPPs!

Continuing to the `test` region, the file concludes:
``` python
...
## test ##
from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

def score_cases(student_fn, ref_fn, *cases):
    proportion_correct = 0
    for case in cases:
        user_val = Feedback.call_user(student_fn, *case)
        ref_val = ref_fn(*case)
        if user_val == ref_val:
            proportion_correct += 1
    proportion_correct /= len(cases)

    Feedback.set_score(proportion_correct)

class Test(PLTestCase):
    @points(2)
    @name("example cases")
    def test_0(self):
        score_cases(self.st.is_sublist, self.ref.is_sublist,
            (['a', 'b', 'c', 'd'], ['b', 'c']),
            ([1, 2, 3, 4], [4, 3])
        )

    
    @points(8)
    @name("advanced cases")
    def test_1(self):
        score_cases(self.st.is_sublist, self.ref.is_sublist,
            ([1, 2, 3, 4], [2, 3]),
            ([1, 2, 3, 4], [3, 2]),
            ([1, 2, 3, 4], []),
            ([1, 2, 3, 4], [1, 2, 3, 4]),
            ([1, 2, 3, 4], [1, 2, 3, 4, 5]),
        )
## test ##
```
If the `## test ##` does not **start and end** before the end of the file or the start of the next region, there will be a syntax error!

[The proper way to write test methods is in prairielearn's developer guide.](https://prairielearn.readthedocs.io/en/latest/python-grader/#teststestpy)

At a glance:
 - Performance is evaluated and transmitted through the class `Feedback`.
 - Test functions must...
     - be methods on a class that extends `PLTestCase
     - be named `test_...`
     - have the `@points` and `@name` decorators
     - call `Feedback.set_score` **on a value between [0, 1]**
 - Any printing done by the student will automatically be relayed to them in the grading section, but we highly discourage grading printed output.

Common Gotchas:
 - Setting the highest possible points value for a test function is done through `@points`, and the performance is entered on a 0-to-1 scale through `Feedback.set_score`. 
 **Entering the number of points recieved will not work!**
 - Test helper functions (ie `score_cases` in the example above) **cannot** be methods (static or instance) on the Test class. 
 They must be defined in a different scope.
