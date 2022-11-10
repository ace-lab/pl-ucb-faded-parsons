# Faded Parsons development

This bogus course is only for working on the `pl-faded-parsons`
element.

It's not a real course. Don't add questions here.

## Cloning Properly

This repo uses submodules, so a special command is required to fully clone.
``` sh
$ git clone --recurse-submodules https://github.com/ace-lab/pl-ucb-faded-parsons.git
```

If you did not add the --recurse-submodules flag, **we recommend you delete and re-clone.**

## Updating the Faded Parsons Element

To pull the latest version of the Faded Parsons element, use:
``` sh
$ git submodule update --remote ./elements/pl-faded-parsons/
```
