# -*- coding: utf-8 -*-
'''
Performance test for image access and cell tracking
'''
__author__ = 'Copyright (C) 2012, Olivier Debeir <odebeir@ulb.ac.be>'


from ivctrack.reader import ZipSource
from ivctrack.helpers import timeit
from ivctrack.cellmodel import Cell

from time import sleep

def benchmark_access():
    """Test function: evaluate the computation time for image access
    """

    @timeit
    def access():

        datazip = '../test/data/seq0_extract.zip'
        reader = ZipSource(datazip)
        g = reader.generator()

        for i,im in enumerate(g):
            pass
        print '#frames:',i,' frame size:',im[1].shape
    access()

def benchmark_process():
    """Test function: evaluate the computation time for cell tracking
    """
    @timeit
    def process():

        datazip = '../test/data/seq0_extract.zip'
        reader = ZipSource(datazip)
        g = reader.generator()

        cellLocations = [(221,184),(408,158),(529,367)]
        params = {'N':16,'radius_halo':30,'radius_soma':15}

        cell_list = [ Cell(x0,y0,**params)  for x0,y0 in cellLocations ]

        for i,im in enumerate(g):
            for c in cell_list:
                c.update(im[1])
        print '#frames:',i,' #cells:',len(cell_list)
    process()

if __name__ == "__main__":

    benchmark_access()
    benchmark_process()
