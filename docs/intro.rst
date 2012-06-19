=============
Installation
=============

Setup requirement
-----------------------------
Some dependencies are needed in order to run ivctrack programs.
Basically for the tracking itself, numpy and scipy are used (including weave inline C-compilation function).

It uses also `h5py <http://code.google.com/p/h5py/>`_ for recording the tracks into one single HDF5 file.

For some examples, `matplotlib <http://matplotlib.sourceforge.net/index.html>`_ is used.

For some graphical user interfaces, `chaco <http://code.enthought.com/projects/chaco/>`_
and
`traits <http://docs.enthought.com/traitsui/traitsui_user_manual/index.html>`_ are required.

Fo some test functions `mencoder <http://www.mplayerhq.hu/design7/news.html>`_ is used to make a movie from separate .png files.


Download
-----------------------------

Getting the distribution:

* download the distribution file :download:`ivctrack-0.1.0.tar.gz <../dist/ivctrack-0.1.0.tar.gz>`

* from the source repository: `Bitbucket <https://bitbucket.org/odebeir/ivctrack/>`_


Author's project website: `<http://homepages.ulb.ac.be/~odebeir/ivctrack>`_


Setup
-----------------------------

* unzip the distribution file in some location

* and run the following command from a terminal at that same location::

    python setup.py install

* now the module should be available in your python environment
    the following code track some cells on the complete sequence, result is save into a HDF5 file
    the appropriate data path should be given (see test_experiment function)

.. code-block:: python

    from ivctrack.cellmodel import test_experiment

    test_experiment()

Test data
-----------------------------
Some test data can be downloaded here:

* :download:`single phase contrast frame (.JPG) <../test/data/exp0001.jpg>`

* :download:`some marks for the first sequence frame (.CSV) <../test/data/fwd_marks.csv>`

* :download:`some marks for the last sequence frame (.CSV) <../test/data/rev_marks.csv>`

* :download:`small zipped phase contrast sequence (30 frames) (.ZIP) <../test/data/seq0_extract.zip>`
