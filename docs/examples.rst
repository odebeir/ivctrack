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


.. ipython::

   In [133]: import numpy.random

   @suppress
   In [134]: numpy.random.seed(2358)

   @doctest
   In [135]: numpy.random.rand(10,2)
   Out[135]:
   array([[ 0.64524308,  0.59943846],
	  [ 0.47102322,  0.8715456 ],
	  [ 0.29370834,  0.74776844],
	  [ 0.99539577,  0.1313423 ],
	  [ 0.16250302,  0.21103583],
	  [ 0.81626524,  0.1312433 ],
	  [ 0.67338089,  0.72302393],
	  [ 0.7566368 ,  0.07033696],
	  [ 0.22591016,  0.77731835],
	  [ 0.0072729 ,  0.34273127]])


.. ipython::
   :suppress:

   In [144]: from pylab import *

   In [145]: ion()

.. ipython::

   @savefig plot_simple.png width=10in
   In [151]: plot([1,2,3]);

   # use a semicolon to suppress the output
   @savefig hist_simple.png width=4in
   In [151]: hist(numpy.random.randn(10000), 100);

