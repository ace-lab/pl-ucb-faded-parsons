def poly(coeffs, x): #0given
total = 0 #1given
for power, coeff in enumerate(coeffs): #1given
print(total) #2given
total = total + coeff * (x ** power) #2given
return total #1given
