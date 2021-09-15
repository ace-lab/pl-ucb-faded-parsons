""" Make a function <code>square_color</code> that tells if a chess 
    square is black based off of its position (see the labeled board below).

    <br>

    <img src="https://www.dummies.com/wp-content/uploads/201843.image0.jpg" 
        alt="chessboard" 
        style="margin-left:auto; margin-right:auto; display:block; width:50;"
    >
"""

## setup_code ##
def to_coordinates(pos: str) -> tuple[int, int]:
    """ Turns a file and rank string and turns it into an (int, int),
        eg 'a1' -> (0, 0), 'd6' -> (3, 5)
    """
    f_ord, r_ord = tuple(map(ord, pos[:2]))
    return f_ord - ord('a'), r_ord - ord('1')
## setup_code ##

def square_color(pos): #0given
    file, rank = to_coordinates(pos)
    black_first_square = file % ?2? == 0
    same_as_first = rank % ?2? == 0
    return black_first_square == same_as_first

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
        score_cases(self.st.square_color, self.ref.square_color,
            ('a1',),
            ('d6',)
        )

    
    @points(8)
    @name("advanced cases")
    def test_1(self):
        score_cases(self.st.square_color, self.ref.square_color,
            *((f + str(r),) for f in 'abcdefg' for r in range(1, 9))
        )
## test ##
