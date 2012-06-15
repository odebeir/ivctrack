# -*- coding: utf-8 -*-
'''
Track cells using

* Meanshift

* Integral shift (todo)

'''
__author__ = 'Olivier Debeir'

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
            xy= tracks[t]['center'][:,1:3]
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


def test_track():
    """Test function: track some cells in a small sequence, compile cell positions into a Track object
    """
    #define sequence source
    #    datazip = '../tests/data/seq0_extract.zip'
    datazip = '../test/data/seq0.zip'
    reader = ZipSource(datazip)

    #mark initial cell position (may be in the middle of the sequence
    cellLocations = [(221,184),(408,158),(529,367)]
    params = {'N':32,'radius_halo':30,'radius_soma':15}
    track_list = []
    for x0,y0 in cellLocations:
        t = Track(x0=x0,y0=y0, model=Cell, frame0=0,params=params)
        track_list.append(t)

        #process the tracking in both fwd and rev directions
    #    for read_dir in ['fwd','rev']:
    for read_dir in ['fwd']:
        g = reader.generator(read_dir=read_dir,first_frame=0,last_frame=100)
        #reset Cell to mark position before changing tracking direction
        for t in track_list:
            t.reset_cell_pos()
        for frame,im in g:
            print frame
            for t in track_list:
                t.update(frame,im,read_dir)

    #post process the records
    for t in track_list:
        t.export()
        print 'track range ',t.frame_range,',', len(t.rec), ' rec available'

    #plot centered celltracks
    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    g = reader.generator(read_dir='fwd',first_frame=0,last_frame=100)
    for frame,im in g:
        ax.imshow(im)
        for t in track_list:
            x = t.data_center[:frame,0]
            y = t.data_center[:frame,1]
            ax.plot(x,y,'-')

        ax.set_xlim([100,300])
        ax.set_ylim([100,250])
        plt.draw()
        sleep(.01)
        plt.savefig('../test/temp/snp%04d.png'%frame)

        plt.cla()


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
        CellUi(c).draw(ax)

    plt.show()

def test_N():
    """Test function: illustrate the N parameter (#of pies of the model)
    """
    im = imread(os.path.join(os.path.dirname(__file__),'../test/data/exp0001.jpg'))
    cellLocations = [(340,190),(474,331),(120,231)]
    for N in [3,5,8,16,32]:
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
#    test_track()
    test_N()
#     test_sequence()
#    make_movie('../tests/temp/snp*.png',out='../tests/temp/movie.avi')
#    test_annotate()
