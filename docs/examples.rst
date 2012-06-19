===========
Examples
===========

.. note:: under construction

Browse the input source
-----------------------------

Set initial marks
-----------------------------

Track a sequence
-----------------------------

Import HDF5 data
-----------------------------

Plot trajectories
-----------------------------

Extract statistics
-----------------------------

Adjust model parameters
-----------------------------

Adaptive cell model
-----------------------------

example

.. ipython::

   In [136]: x = 2

   In [137]: x**3
   Out[137]: 8


.. ipython::

  In [138]: z = x*3   # x is recalled from previous block

  In [139]: z
  Out[139]: 6

  In [140]: print z
  --------> print(z)
  6

  In [141]: q = z[)   # this is a syntax error -- we trap ipy exceptions
  ------------------------------------------------------------
     File "<ipython console>", line 1
       q = z[)   # this is a syntax error -- we trap ipy exceptions
	     ^
  SyntaxError: invalid syntax
