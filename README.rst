ivctrack Module Repository
==========================

This project is a Python module for in-vitro cell tracking.

http://homepages.ulb.ac.be/~odebeir/ivctrack/

the following document describes a minimal setup

the gui options should be considered as far as experimental and may be problematic depending on the backends

Dependencies
============

needs a minimal python stack, e.g.

Anaconda Python distribution http://www.continuum.io/downloads


HDF5 viewer
============

tracked sequence files (.hdf5) can be viewed with HDFView :
http://www.hdfgroup.org/hdf-java-html/hdfview/index.html#download_hdfview

Get the sources
===============

git clone https://github.com/odebeir/ivctrack

Get an example sequence
=======================

http://homepages.ulb.ac.be/~odebeir/ivctrack/_downloads/seq0_extract.zip

http://homepages.ulb.ac.be/~odebeir/ivctrack/_downloads/fwd_marks.csv

http://homepages.ulb.ac.be/~odebeir/ivctrack/_downloads/rev_marks.csv


test data can be moved into a data dir e.g.

in ivctrack/test/ create a subdir /data and a subdir /temp for results

  > cd ivctrack/test
  
  > mkdir data
  
  > mkdir temp

copy the downloaded file there (in data)


Installation
=============

installation step is needed if you want to add the ivctrack module as a local available module in the current python environnement

for the momentn just skip the setup step from the homepage/install and change to the ivctrack/ivctrack dir

  > cd ivctrack/ivctrack

Running the code
=====================

simple tracking test
--------------------

  > python cellmodel.py

now the subdir temps should contain a file : 

test_fwd.hdf5

this test also create a defaults_parameters.json in the current directory that can be used as parameters file (editable)

test the command line function:
-------------------------------

  > python ivct_cmd.py -h

  usage: IVCT_CMD [-h] {test,mark,track,play,gui,plot,export} ...

  optional arguments:
    -h, --help            show this help message and exit

  subcommands:
    valid subcommands
  
    {test,mark,track,play,gui,plot,export}
                          additional help (e.g. type "ivct_cmd track --help").
      test                test a zipped sequence file
      mark                marks the n-th frame of a zipped sequence file, save
                          marks in a .csv file
      track               track a zipped sequence file using marks
      play                play a tracked sequence
      gui                 display a graphical interactive view for model
                          parameters fitting
      plot                plot a tracked sequence
      export              export a tracked sequence

test a zipped sequence data file
---------------------------------

  > python ivct_cmd.py test --seq ../test/data/seq0_extract.zip

  MODE: test
  ../test/data/seq0_extract.zip
  <reader.ZipSource object at 0x10053c810>../test/data/seq0_extract.zip first:1 last:30 #:30

remark:

the first time the program is executed, some optimized functions are compiled, therefore, it is possible that the function stall
a cache mechanisms exists, so the next call to the function skip the compilation step and should run without notice.

track the test sequence (fwd direction using marks on the first frame)
----------------------------------------------------------------------

  > python ivct_cmd.py track --seq ../test/data/seq0_extract.zip --marks ../test/data/fwd_marks.csv --params ../test/data/parameters.json  --hdf5 ../test/temp/track.hdf5

the trajectories are saved in a given hdf5 filename or in 

track.hdf5 

in currrent path



*From here it may be problem with the backend an qt install (e.g. on mac) this is to be fixed*

if you have installed Anaconda 1.6.1 (x86_64)/Python 2.7.5, the following package should be installed (for guis see below)

  > pip install wx

open a gui for the test sequence
--------------------------------

  > python ivct_cmd.py gui --seq ../test/data/seq0_extract.zip


