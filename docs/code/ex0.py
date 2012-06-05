# -*- coding: utf-8 -*-
# display a sample cell

import matplotlib.pyplot as plt
import numpy as npy

import context
from ivctrack.reader import ZipSource,Reader

datazip_filename = '../../tests/data/seq0_extract.zip'

reader = Reader(ZipSource(datazip_filename))

ima = reader.getframe()

plt.figure()
plt.imshow(ima[400:490,170:230],cmap=plt.cm.gray)
plt.colorbar()
plt.show()