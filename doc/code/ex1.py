# -*- coding: utf-8 -*-
# display a sample cell

import matplotlib.pyplot as plt
import numpy as npy

import context
from ivctrack.reader import ZipSource,Reader

datazip = '../../test/data/seq0_extract.zip'

reader = Reader(ZipSource(datazip))
ima = reader.getframe()

plt.figure()
plt.imshow(ima[400:490,170:230],cmap=plt.cm.gray)
plt.colorbar()
plt.show()