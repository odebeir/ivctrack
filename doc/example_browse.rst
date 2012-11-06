Browse the input source
-----------------------------

The following example illustrates how to access frame sequence contained inside a simple .zip file, each individual
image is named exp0001.zip , exp0002.zip etc.

.. ipython::

    In [9]: datazip_filename = '../test/data/seq0_extract.zip'

    In [11]: from ivctrack.reader import ZipSource,Reader

    In [12]: reader = Reader(ZipSource(datazip_filename))

    In [13]: reader.getframe()

    In [15]: reader.moveto(1)



Read marks from .CSV file
-----------------------------

.. ipython::

    In [6]: from ivctrack.cellmodel import import_marks

    In [7]: marks = import_marks('../test/data/fwd_marks.csv')

    In [8]: marks
