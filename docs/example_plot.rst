Plot tracking results
-----------------------------

Plot the trajectories saved in an HDF5 file

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: feat,data = get_hdf5_data('../test/temp/test.hdf5')

    In [40]: plt.figure()

    In [39]: for d in data:
       ....:     t = d['center']
       ....:     plt.plot(t[:,0],t[:,1])

    In [40]: plt.xlabel('x')

    In [40]: plt.ylabel('y')

    @savefig plot_tracks.png width=4in
    In [40]: plt.show()

Plot the x position with respect to the frame number

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: feat,data = get_hdf5_data('../test/temp/test.hdf5')

    In [40]: plt.figure()

    In [39]: for d in data:
       ....:     f = d['frames']
       ....:     t = d['center']
       ....:     plt.plot(f,t[:,0])

    In [40]: plt.xlabel('frame')

    In [40]: plt.ylabel('x')

    @savefig plot_tracks_t.png width=4in
    In [40]: plt.show()

Plot the trajectories relatively to there origin

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: feat,data = get_hdf5_data('../test/temp/test.hdf5')

    In [40]: plt.figure()

    In [39]: for d in data:
       ....:     t = d['center']
       ....:     plt.plot(t[:,0]-t[0,0],t[:,1]-t[0,1])

    In [40]: plt.xlabel('$x_{rel}$')

    In [40]: plt.ylabel('$y_{rel}$')

    In [40]: plt.axvline(x=0,color='grey')

    In [40]: plt.axhline(y=0,color='grey')

    @savefig plot_tracks_rel.png width=4in
    In [40]: plt.show()

Extract cell shape from HDF5 file

.. ipython::

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [9]: feat,data = get_hdf5_data('../test/temp/test.hdf5',fields=['center','halo','soma'])

    In [99]: for k,f in feat.iteritems():
       ....:     print k,f

    In [40]: plt.figure()

    In [39]: for d in data:
       ....:     t = d['halo']
       ....:     plt.plot(t[0,:,0],t[0,:,1],'o')
       ....:     t = d['soma']
       ....:     plt.plot(t[0,:,0],t[0,:,1])

    In [40]: plt.xlabel('$x_{rel}$')

    In [40]: plt.ylabel('$y_{rel}$')

    @savefig plot_tracks_shape.png width=4in
    In [40]: plt.show()


Fill the background with phase contrast image

.. ipython::

    In [9]: datazip_filename = '../test/data/seq0_extract.zip'

    In [11]: from ivctrack.reader import ZipSource,Reader

    In [3]: from ivctrack.hdf5_read import get_hdf5_data

    In [41]: import matplotlib.pyplot as plt

    In [41]: import matplotlib.cm as cm

    In [12]: reader = Reader(ZipSource(datazip_filename))

    In [13]: bg = reader.getframe()

    In [9]: feat,data = get_hdf5_data('../test/temp/test.hdf5',fields=['center','halo','soma'])

    In [40]: plt.figure()

    In [40]: plt.imshow(bg,cmap=cm.gray)

    In [39]: for d in data:
       ....:     t = d['halo']
       ....:     plt.plot(t[0,:,0],t[0,:,1],'o')
       ....:     t = d['soma']
       ....:     plt.plot(t[0,:,0],t[0,:,1])

    In [40]: plt.xlabel('$x_{rel}$')

    In [40]: plt.ylabel('$y_{rel}$')

    @savefig plot_tracks_bg.png width=8in
    In [40]: plt.show()



