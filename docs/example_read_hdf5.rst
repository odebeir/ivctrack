Read HDF5 data
-----------------------------

Print the content of an HDF5 file

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_info

    In [9]: get_hdf5_info('../test/temp/test.hdf5')

Extract the x,y position of all the tracks

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: data = get_hdf5_data('../test/temp/test.hdf5',fields=['center'])

    In [40]: plt.figure()

    In [39]: for d in data:
       ....:     frames = d['frames']
       ....:     t = d['center']
       ....:     print t.shape

    In [39]: print frames

    In [39]: print t



Extract cell shape from HDF5 file

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: data = get_hdf5_data('../test/temp/test.hdf5',fields=['center','halo','soma'])

    In [39]: for d in data:
       ....:     h = d['halo']
       ....:     s = d['soma']
       ....:     print h.shape


