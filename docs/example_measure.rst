Trajectory analysis
-----------------------------

Cell speed analysis : average speed, MRDO and hull speed :

.. ipython::

    In [28]: import matplotlib.pyplot as plt

    In [32]: from ivctrack.hdf5_read import get_hdf5_data

    In [32]: from ivctrack.measurement import speed_feature_extraction

    In [9]: hdf5_filename = '../test/data/test_rev.hdf5'

    In [10]: c_feat,c_data = get_hdf5_data(hdf5_filename,fields=['center'])

    In [29]: feat,data = speed_feature_extraction(c_data)

    In [30]: print feat

    In [31]: plt.scatter(data[:,1],data[:,3])

    In [31]: plt.xlabel('avg speed')

    In [31]: plt.ylabel('hull speed')

    @savefig plot_measure1.png width=4in
    In [34]: plt.draw()

    In [34]: plt.figure()

    In [31]: plt.hist(data[:,1:4])

    In [31]: plt.legend(['avg','mrdo','hull speed'])

    @savefig plot_measure2.png width=4in
    In [34]: plt.draw()
