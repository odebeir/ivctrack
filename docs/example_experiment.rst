Track an experiment and save results to HDF5
---------------------------------------------

The example initialise a reader pointing to a .zipped sequence, reads initial cell position from a .csv file.
an experiment object is created, this object manage the complete list of tracks for the sequence.
The tracking is done in the forward direction (since the marks are defined for the first frame).
The experiment is then written in a HDF5 file

.. ipython::

    In [28]: from ivctrack.reader import ZipSource,Reader

    In [32]: from ivctrack.cellmodel import Cell,Experiment,Track

    In [9]: datazip_filename = '../test/data/seq0_extract.zip'

    In [29]: reader = Reader(ZipSource(datazip_filename))

    In [7]: marks = import_marks('../test/data/fwd_marks.csv')

    In [59]: experiment = Experiment(reader,exp_name='Test')

    In [60]: params = {'N':8,'radius_halo':20,'radius_soma':12,'exp_halo':10,'exp_soma':2,'niter':10,'alpha':.75}

    In [56]: for x0,y0,frame0 in marks:
       ....:     t = Track(x0=x0,y0=y0,frame0=frame0,model=Cell,params=params)
       ....:     experiment.add_track(t)

    In [57]: experiment.do_tracking('fwd')

    In [58]: experiment.save_hdf5('../test/temp/test.hdf5')



