=============
Installation
=============

Setup requirement
-----------------------------
Some dependencies are needed in order to run ivctrack programs.
Basically for the tracking itself, numpy and scipy are used (including weave inline C-compilation function).

For some examples, Matplotlib is used.

For some graphical user interfaces, chaco and traits are required.

Fo some test functions mencoder is used to make a movie from separate .png files.


Download
-----------------------------

Getting the distribution:

* `ivctrack-0.1.0.tar.gz <../dist/ivctrack-0.1.0.tar.gz>`

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

