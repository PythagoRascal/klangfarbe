# Freqs C0 - C8
freqs = [440 * (2**(x / 12.0)) for x in range(-57, 40)]
#print freqs

import math
base = 2**(1/12.0)
freqToPitch = [int(round(math.log(x / 440.0, 2**(1/12.0)))) for x in range(1, 48000)]
print freqToPitch
