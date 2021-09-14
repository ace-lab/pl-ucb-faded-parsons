""" Make a function <code>is_sublist</code> that checks wether the first
    argument contains the second as a sublist (including ordering), eg

    <pl-code language="python" highlight-lines="2,4,6">
    is_sublist(['a', 'b', 'c', 'd'], ['b', 'c'])
    True
    is_sublist([1, 2, 3, 4], [4, 3])
    False</pl-code>
"""

def is_sublist(list, sublist): #0given
    n, m = len(list), len(sublist)
    for i in range(?n - m?):
        start, end = i, i + m
        if list[?start:end?] == sublist:
            return ?True?
    return False #1given

## test ##
from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

def test_cases(student_fn, ref_fn, cases):
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
    @name("testing example cases")
    def test_0(self):
        test_cases(self.st.is_sublist, self.ref.is_sublist, [
            [['a', 'b', 'c', 'd'], ['b', 'c']],
            [[1, 2, 3, 4], [4, 3]]
        ])

    
    @points(8)
    @name("advanced cases")
    def test_1(self):
        test_cases(self.st.is_sublist, self.ref.is_sublist, [
            [[1, 2, 3, 4], [2, 3]],
            [[1, 2, 3, 4], [3, 2]],
            [[1, 2, 3, 4], []],
            [[1, 2, 3, 4], [1, 2, 3, 4]],
            [[1, 2, 3, 4], [1, 2, 3, 4, 5]],
        ])
## test ##
