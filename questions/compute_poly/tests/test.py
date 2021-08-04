from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback
import numpy as np


class Test(PLTestCase):

    @points(1)
    @name("testing single case")
    def test_0(self):
        case = [[10], 3]
        points = 0
        user_val = Feedback.call_user(self.st.poly, *case)
        ref_val = self.ref.poly(*case)
        if Feedback.check_scalar(f"args: {case}", ref_val, user_val):
            points += 1
        Feedback.set_score(points)

    @points(4)
    @name("testing multiple cases")
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
        Feedback.set_score(points/len(cases))