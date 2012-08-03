# -*- coding: utf-8 -*-
# display a sample cell

import matplotlib.pyplot as plt
import numpy as npy

import context
from test import test_N
from ivctrack.cellmodel import AdaptiveCell

test_N(n_list=[16],model=AdaptiveCell)