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

Source repository: `Bitbucket <https://bitbucket.org/odebeir/ivctrack/>`_

Author's project website: `<http://homepages.ulb.ac.be/~odebeir/ivctrack>`_


Setup
-----------------------------

* unzip the distribution file in some location

* and run the following command from a terminal at that same location::

    python setup.py install

* now the module should be available in your python environment e.g.

.. code-block:: python

    from ivctrack import

    todo !

