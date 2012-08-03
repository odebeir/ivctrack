# -*- coding: utf-8 -*-
# display a sample cell

import matplotlib.pyplot as plt
import numpy as npy

import context
from test import test_N

plt.subplot(1,2,1)
test_N(n=16,soma=False)
plt.subplot(1,2,2)
test_N(n=16,halo=False)

plt.show()