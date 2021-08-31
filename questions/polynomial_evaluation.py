"""Write a function <code>poly</code> that calculates the values of a 
polynomial with the given coefficients at the given value of <code>x</code>,
ie, evaluate $$f(x) = \sum_i \textrm{coeffs}_i ~ x^i$$"""

## setup_code ##
a = 3
b = a + 4
## setup_code ##

def poly(coeffs, x): #0given
    # Keep track of the total as we iterate through each term.
    # Each term is of the form coeff*(x**power).
    total = ?0? #blank test #1given # total starts at 0
    
    # Extract the power and coefficient for each term.
    for power, coeff in enumerate(coeffs):
        # Add the value of the term to the total.
        ?total? = total + coeff * (x ** power) #2given
    return total #1given

## test ##
from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

class Test:
    pass

## test ##