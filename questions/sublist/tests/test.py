from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

def score_cases(student_fn, ref_fn, *cases):
    proportion_correct = 0
    for case in cases:
        user_val = Feedback.call_user(student_fn, *case)
        ref_val = ref_fn(*case)
        if Feedback.check_scalar(f"args: {case}", ref_val, user_val):
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