def poly(coeffs, x): #0given
total = !BLANK #1given
for power, coeff in enumerate(coeffs): #1given
total = total + coeff * (x ** power) #2given
return total #1given
