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

This tool will search for a provided path in ./ questions/ ../../questions/ and ../../ before erring.
If none is provided, it will hunt for a questions directory, and use all .py files there.
 
### Semantic Rules
 - If the file begins with a docstring, it will become the question text
     - The question text is removed from the answer
     - Docstrings are always removed from the prompt
 - Text surrounded by `?`s will become blanks in the prompt
     - Blanks cannot span more than a single line
     - The text within the question marks fills the blank in the answer
     - `?`s in any kind of string-literal or comment are ignored
 - Comments are removed from the prompt unless the comment matches the form `#{n}given` or `#blank`
     - These special forms are the only comments removed from the answer
 - Regions are begun and ended by `## {region name} ##`
     - A maximum of one region may be open at a time
     - Regions must be closed before the end of the source
     - All text in a region is only copied into that region
     - Text will be copied into a new file with the regions name in the
       question directory, excluding these special regions:
         explicit: `test` `setup_code`
         implicit: `answer_code` `prompt_code` `question_text`
     - Code in `setup_code` will be parsed to extract exposed names unless the --no-parse
       flag is set. Type annotations and function docstrings are used to fill out server.py
     - Any custom region that clashes with an automatically generated file name
       will overwrite the automatically generated code
 - Import regions allow for the contents of arbitrary files to be loaded as regions
     - They are formatted as `## import {rel_file_path} as {region name} ##`
        where `rel_file_path` is the relative path to the file from the source file
     - Like regular regions, they cannot be used inside of another region