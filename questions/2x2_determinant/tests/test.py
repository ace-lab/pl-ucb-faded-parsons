from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback


class Test(PLTestCase):
    @points(1)
    @name("test 0")
    def test_0(self):
        case = [1, 2, 3, 4]
        user_val = Feedback.call_user(self.st.det, *case)
        ref_val = self.ref.det(*case)
        points = 0
        if Feedback.check_scalar(f'case: {case}', ref_val, user_val):
            points += 1
        Feedback.set_score(points)