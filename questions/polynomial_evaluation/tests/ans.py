


def poly(coeffs, x): 
    # Keep track of the total as we iterate through each term.
    # Each term is of the form coeff*(x**power).
    total = 0 # total starts at 0
    
    # Extract the power and coefficient for each term.
    for power, coeff in enumerate(coeffs):
        # Add the value of the term to the total.
        total = total + coeff * (x ** power) 
    return total 
from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

@names_from_user()
@names_from_setup(, )
class Test:
    pass