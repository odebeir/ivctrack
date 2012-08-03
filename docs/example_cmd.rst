Command line operations
-----------------------------

A command line is available for some of the basic operations such as create a file that contains marks,
adjusting tracking parameters (through a .json file), visualizing the tracking results, etc.

The main command line module is IVCT_CMD, called with python such as:

.. code-block:: none

    > python ivct_cmd.py gui --seq seq0_extract.zip

Generic help

.. program-output:: python ../ivctrack/ivct_cmd.py --help

Tracking of a sequence

.. program-output:: python ../ivctrack/ivct_cmd.py track --help

Interactive cell-marking

.. program-output:: python ../ivctrack/ivct_cmd.py mark --help

Testing the validity of a sequence

.. program-output:: python ../ivctrack/ivct_cmd.py test --help

Playing a tracked sequence

.. program-output:: python ../ivctrack/ivct_cmd.py play --help

Plotting trajectory results

.. program-output:: python ../ivctrack/ivct_cmd.py plot --help

Exporting data

.. program-output:: python ../ivctrack/ivct_cmd.py export --help

Experimental graphic user interface using chaco:

.. program-output:: python ../ivctrack/ivct_cmd.py gui --help