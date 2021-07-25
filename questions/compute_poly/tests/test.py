from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback
import numpy as np


class Test(PLTestCase):

    @points(1)
    @name("Test [[10], 3]")
    def test_0(self):
        user_val = Feedback.call_user(self.st.poly, [10], 3)
        if Feedback.check_scalar("poly([10], 3)", self.ref.poly([10], 3), user_val):
            Feedback.set_score(1)
        else:
            Feedback.set_score(0)

    @points(4)
    @name("testing multiple")
    def test_1(self):
        cases = [
            [[4, 5], 2],
            [[2, 4, 7], 6],
            [[2, 4, 7], 1],
            [[1,2,3,4,5,6], 7]
        ]
        points = 0
        for case in cases:
            user_val = Feedback.call_user(self.st.poly, *case)
            ref_val = self.ref.poly(*case)
            if Feedback.check_scalar(f"args: {case}", ref_val, user_val):
                points += 1
        Feedback.set_score(points)