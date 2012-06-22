.. ivctrack documentation master file, created by
   sphinx-quickstart on Mon Apr 16 21:22:43 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to *ivctrack*'s documentation.
======================================

.. figure:: image/screenshot1.png
    :scale: 70 %
    :alt: in vitro cell tracking
    :align: right
    :figwidth: 45%

    Example of the tracking model adjusted on a cell observed under phase contrast microscopy.

IVCTRACK stands for in vitro cell tracking toolbox.

This documentation support a set of python programs dedicated to in vitro cell tracking. More specifically for
tracking cell seeded on 2D containers and observed under classical phase contrast microscopy.

In vitro cell tracking is one tool for cell motility observation both qualitatively and quantitatively.

The implemented method presented here is a tentative of python porting of previous code written for Matlab. This method
was used in several publications for cell speed measurement [deb05]_ and cell chemotactism analysis [deb04]_ .

License
==================

This project is published under GPL v3 license.

Features
==================

* zipped sequence of images (.png,...)

* tracking using multiple meanshift kernels

* both forward and reverse tracking

* results saved into a single HDF5 per sequence

* speed statistics

Roadmap
==================

* stabilizing a first version, with a basic documentation, adding more examples

* developing a second tracking model which take into account possible cell shape changes (adaptive model)

* testing a meanshift based on integral image

* developing GUIs for cell marking, interactive result visualization

* adding statistical trajectory analysis


==========================================================================

Video example :

* `Hi-resolution tracking example <http://www.youtube.com/watch?list=UUDj1Oeqc8ICa-P0l7pQjoQA&feature=player_detailpage&v=IOlPvcS4pRI>`_

* `Example of a mitosis tracked in reverse time <http://www.youtube.com/watch?list=UUDj1Oeqc8ICa-P0l7pQjoQA&feature=player_detailpage&v=T_88S9S3F6c>`_


==========================================================================

Content
===========

.. list-table::
   :widths: 100 200 200
   :header-rows: 0

   * - .. toctree::
          :maxdepth: 2

          intro.rst
          install.rst
          about.rst
     - .. toctree::
          :maxdepth: 2

          examples.rst
     - .. toctree::
          :maxdepth: 2

          modules.rst
          references.rst
   * - * :ref:`genindex`
       * :ref:`modindex`
       * :ref:`search`
     -
     -
