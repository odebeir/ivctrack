# -*- coding: utf-8 -*-
'''
Track cells using

* Meanshift

* Integral shift (todo)

'''
__author__ = 'Copyright (C) 2012, Olivier Debeir <odebeir@ulb.ac.be>'

import os
import matplotlib.pyplot as plt
import numpy as npy
from scipy.misc import imread

from ivctrack.cellmodel import Cell,Track,Experiment
from ivctrack.meanshift import LUT,generate_triangles,generate_inverted_triangles,meanshift,meanshift_features
from ivctrack.reader import ZipSource,Reader
from ivctrack.helpers import make_movie,timeit
from ivctrack.mpl_ui import CellUi

from time import sleep
import h5py


class SimplePlayer(object):
    """open a reader and a hdf5experiment
    plot results
    """
    def __init__(self,reader,hdf5filename):
        self.reader = reader
        self.hdf5filename = hdf5filename
        self.fid = h5py.File(hdf5filename, 'r')

        plt.figure()
        self.plot_bg()
        self.plot_tracks()
        self.plot_halo()
        plt.show()

    def plot_bg(self):
        frame,im = self.reader.generator().next()
        plt.imshow(im)

    def plot_tracks(self):
        tracks = self.fid['tracks']
        for t in tracks:
            xy= tracks[t]['center']
            plt.plot(xy[:,0],xy[:,1])

    def plot_halo(self):
        tracks = self.fid['tracks']
        for t in tracks:
            xy= tracks[t]['halo'][0,:,0:2]
            plt.plot(xy[:,0],xy[:,1],'o')

def test_player():
    """reopen an HDF5 file
    """
    datazip = '../test/data/seq0.zip'
    reader = ZipSource(datazip)
    hdf5filename = '../test/temp/test.hdf5'

    player = SimplePlayer(reader,hdf5filename)


def test_static():
    """Test function: apply meanshift on several cell in one single frame
    """
    im = imread('../test/data/exp0001.jpg')
    cellLocations = [(340,190),(474,331),(120,231)]

    params = {'N':64,'radius_halo':30,'radius_soma':15}
    cell_list = [ Cell(x0,y0,**params)  for x0,y0 in cellLocations ]

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    ax.imshow(im, interpolation='nearest')

    for c in cell_list:
        c.update(im)
        CellUi(c,ax).draw(ax)

    plt.show()

def test_N(n_list=[3,5,8,16,32]):
    """Test function: illustrate the N parameter (#of pies of the model)
    """
    im = imread(os.path.join(os.path.dirname(__file__),'../test/data/exp0001.jpg'))
    cellLocations = [(340,190),(474,331),(120,231)]
    for N in n_list:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(im, interpolation='nearest')
        params = {'N':N,'radius_halo':30,'radius_soma':15}
        cell_list = [ Cell(x0,y0,**params)  for x0,y0 in cellLocations ]
        for c in cell_list:
            c.update(im)
            CellUi(c,ax).draw(ax)
            plt.title('#pies = %d'%N)
        ax.set_xlim([300,400])
        ax.set_ylim([100,250])
    plt.show()

def test_sequence():
    """Test function: track some cells in a small sequence, illustration is grabbed to .png files
    """

    datazip = '../test/data/seq0_extract.zip'
    reader = ZipSource(datazip)
    g = reader.generator()

    cellLocations = [(221,184),(408,158),(529,367)]

    params = {'N':32,'radius_halo':30,'radius_soma':10}
    cell_list = [ Cell(x0,y0,**params)  for x0,y0 in cellLocations ]

    fig = plt.figure(1)
    ax = fig.add_subplot(111)


    for frame,im in g:
        ax.imshow(im, interpolation='nearest')

        for c in cell_list:
            c.update(im)
            CellUi(c,ax).draw(ax)

        ax.set_xlim([300,500])
        ax.set_ylim([100,250])
        plt.draw()
        plt.savefig('../test/temp/snp%04d.png'%frame)
        sleep(.01)

        plt.cla()

    make_movie('../test/temp/snp*.png',out='../test/temp/movie.avi')

def test_annotate():
    """Open the first frame of a sequence and wait the user click on initial cell position
    returns a list of positions
    """

    datazip_filename = '../test/data/seq0_extract.zip'
    reader = Reader(ZipSource(datazip_filename))
    ima = reader.moveto(29)
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plt.imshow(ima)
    print '*'*80
    print 'left-click : add , right-click : remove last, middle-click : exit'
    print '*'*80
    xy = plt.ginput(n=0, timeout=0)
    print xy
    params = {'N':16,'radius_halo':30,'radius_soma':15}
    cell_list = [ Cell(x0,y0,**params)  for x0,y0 in xy ]
    for c in cell_list:
        c.update(ima)
        CellUi(c,ax).draw(ax)
    plt.show()



if __name__ == "__main__":

#    test_static()
#    test_player()
#    test_N()
    test_sequence()
#    test_annotate()
