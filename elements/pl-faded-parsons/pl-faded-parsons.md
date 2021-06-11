### `pl-faded-parsons` element

A `pl-faded-parsons` element presents the student with a chunk of code
in which the lines are scrambled and must be placed in the correct
order (Parsons problem).  Some lines may also have blanks substituted for variable
names, keywords, etc. (hence Faded Parsons).

The instructor provides the reference solution, information regarding
what to "fade" and by how much, and one or more tests that are run to
evaluate the student's answer.

The element is based on the work of [Nathaniel
Weinman](https://www.cs.berkeley.edu/~nweinman) at UC Berkeley.

TBD: list contributors who helped with this element's implementation.

#### Sample element

TBD: replace this with a screenshot of the element in action; the png
file should eventually go in `PrairieLearn:PrairieLearn/docs/elements/pl-faded-parsons.png`

![](elements/pl-faded-parsons.png)

```html
<pl-faded-parsons language="py" difficulty="0.3">

  <!-- TBD however we express other attributes/content of the element  -->
  
</pl-faded-parsons>
```

#### Customizations

Attribute | Type | Default | Description
--- | --- | --- | ---
`language`       | string  | "py"       | Language the problem is in, given as the filename extension for files in that language. Currently must be `py` (Python 3).
`answers-name`   | string  | "fp"       | Name of answers dict, only matters if >1 Faded Parsons element in same question
`partial-credit` | boolean | false      | Whether to give partial credit; see below.
`code`           | string  | `code.`_lang_  | Where the code lives under `clientFilesQuestion`, where _lang_ is the value of the `lang` attribute above
`tests`          | string  | `tests.`_lang_ | Where the test files live under `clientFilesQuestion`

#### Example implementations


#### See also

- [`pl-order-blocks` for simple/non-coding problems involving putting things in order](#pl-order-blocks)
