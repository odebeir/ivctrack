=============
Description
=============

Several approaches have been used to tackle in vitro cell tracking with phase contrast imaging. Basically to approaches
are possible [ref are needed]:

* object detection and inter-frame correspondence
    each image af the sequence is analysed, object(cells) are detected and/or segmented, the consecutive cell position
    i.e. the tracking, is achieved by finding the best association between cells detected in frame t and frame t+1.

* model based tracking
    this approach try to adjust model on the t+1 frame starting from the last observed position for the cell in t.

The proposed method in ivctrack belongs to the second approach. The toolbox does not segment the image, it tracks
cells adjusting a model on new frame.

Cell model
-----------------

Similarly to the method described in [deb05]_ the neighborhood of the cell is divided into N triangles centered on the
current cell position. These triangle are attracted by white halos pixels. A second series of smaller triangles oriented
in the opposite direction are attracted by darker somas pixels.

The method consist in iteratively compute the center of gravity (the mean of the mean-shift) for each triangle.

For each iteration, a new cell centroid is computed combining halo ans soma centers.

After a fixed number of iteration, the new cell position is fixed and the next frame is processed.

The method developed in this toolbox is a little bit different from these described in the original paper with respect
to the shape of the inner triangles which are put in a reversed direction. This option gives better results for the soma
detection.

The following figure illustrate how the space around a cell is decomposed into pies (N=8). Large pies are in charge of
finding the halo, smaller inner pies are responsible for the soma.

.. plot:: code/ex2.py



Implementation
------------------

The limiting part of the tracking algorithm is the mean shift computation for each pie of each cell tracker. Therefore,
a C implementation has been done to tackle this specific task.

Results
------------------
The tracking results are saved in a unique HDF5 file, which offers the possibility to include textual comment and
a hierarchical structure. This option enable the interoperability with lot of other languages for which an HDF5 interface
exists.


.. figure:: image/screenshot2.png
    :scale: 70 %
    :alt: HDF5 viewer
    :align: left
    :figwidth: 45%

    Tracking results are available in a HDF5 document
