Update cell position
-----------------------------

.. ipython::

    In [28]: from ivctrack.reader import ZipSource,Reader

    In [32]: from ivctrack.cellmodel import Cell

    In [29]: reader = Reader(ZipSource(datazip_filename))

    In [30]: ima = reader.getframe()

    In [31]: cellLocations = [(340,190),(474,331),(120,231)]

    In [34]: params = {'N':8,'radius_halo':30,'radius_soma':15}

    In [35]: cell_list = [ Cell(x0,y0,**params)  for x0,y0 in cellLocations ]

    In [36]: for c in cell_list:
       ....:     c.update(ima)

    In [38]: for c in cell_list:
       ....:     print c.center