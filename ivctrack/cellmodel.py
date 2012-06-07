# -*- coding: utf-8 -*-
'''This file contains the main Classes definition
'''
__author__ = 'Copyright (C) 2012, Olivier Debeir <odebeir@ulb.ac.be>'
__license__ ="""
pyrankfilter is a python module that implements 2D numpy arrays rank filters, the filter core is C-code
compiled on the fly (with an ad-hoc kernel).

Copyright (C) 2012  Olivier Debeir

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import numpy as npy
from scipy.misc import imread

from ivctrack.meanshift import LUT,generate_triangles,generate_inverted_triangles,meanshift,meanshift_features
from ivctrack.reader import ZipSource,Reader
from ivctrack.helpers import make_movie,timeit

from time import sleep
import h5py

class Cell(object):
    """Cell object, the model is described by:

    * a cell position

    * the number of division (for both outer and inner part)

    * the weight Look Up Table used for the inner (black soma) and for the outer part (white halo)
    """
    def __init__(self,x0,y0,N=16,radius_halo=30,radius_soma=12,exp_halo=10,exp_soma=2,niter=10,alpha=.75):
        #model center
        self.x = x0
        self.y = y0

        #model parameters
        self.N = N
        self.radius_halo = radius_halo
        self.radius_soma = radius_soma
        self.LutW = LUT('white',exp_halo)
        self.LutB = LUT('black',exp_soma)
        self.niter = niter
        self.alpha = alpha

        self.build_triangles()

    def build_triangles(self):
        """Build triangle lists for the Cell model, one for the halo tracking, one for the soma tracking
        """
        self.tri_halo = generate_triangles(self.x,self.y,self.N,self.radius_halo)
        self.tri_soma = generate_inverted_triangles(self.x,self.y,self.N,self.radius_soma)

    def set(self,x,y):
        self.x = x
        self.y = y
        self.build_triangles()

    def update(self,im):
        """Update cell position with respect to a given image
        """

        for iter in range(self.niter):
            #compute the shifts
            self.shift_halo = meanshift(im,self.tri_halo,0.0,0.0,lut = self.LutW)
            self.shift_soma = meanshift(im,self.tri_soma,0.0,0.0,lut = self.LutB)

            #update the position
            #-halo centroid
            halo = npy.asarray([sh[0:2] for sh in self.shift_halo])
            #-nucleus centroid
            soma = npy.asarray([sh[0:2] for sh in self.shift_halo])

            self.x,self.y = (1.-self.alpha) * soma.mean(axis=0) + self.alpha * halo.mean(axis=0)

            #update the triangles
            self.build_triangles()


class Track(object):
    """Object responsible for recording different cell position during time, it also manage the mark positions
    """
    def __init__(self,x0,y0,frame0,model,params):
        self.model = model
        self.params = params
        self.cell = model(x0,y0,**params)
        self.frame0 = frame0
        self.x0 = x0
        self.y0 = y0
        self.frame = frame0
        self.frame_range = [frame0,frame0]      # [first,last] tracked frames
        self.rec = {}                           # data record

    def reset_cell_pos(self):
        self.frame = self.frame0
        self.cell.set(self.x0,self.y0)

    def update(self,frame,im,dir):
        if dir=='fwd':
            if frame == self.frame+1:
                self.cell.update(im)
                self.rec[frame] = ((self.cell.x,self.cell.y),self.cell.shift_halo,self.cell.shift_soma)
                self.frame = frame
                self.frame_range[1] = self.frame

        if dir=='rev':
            if frame == self.frame-1:
                self.cell.update(im)
                self.rec[frame] = ((self.cell.x,self.cell.y),self.cell.shift_halo,self.cell.shift_soma)
                self.frame = frame
                self.frame_range[0] = self.frame

    def export(self):
        """export the rec to numpy array
        """
        L = list(self.rec)
        L.sort()
        halo=[]
        soma = []
        center = []
        for k in L:
            c,h,s = self.rec[k]
            center.append(c)
            halo.append(h)
            soma.append(s)
        self.data_center=npy.asarray(center)
        self.data_halo=npy.asarray(halo)
        self.data_soma=npy.asarray(soma)

class Experiment(object):
    """An experiment keep all track of on sequence together,
    it is responsible for saving tracking result to file
    """
    def __init__(self,reader,exp_name='no_name'):
        self.reader = reader
        self.name = exp_name
        self.track_list = []

    def add_track(self,track):
        self.track_list.append(track)

    def track(self,read_dir,first_frame=0,last_frame=-1):
        r  = self.reader.range()

        #reset Cell to mark position before changing tracking direction
        for t in self.track_list:
            t.reset_cell_pos()
        for frame in r[first_frame:last_frame]:
            print frame
            im = self.reader.moveto(frame)
            for t in self.track_list:
                t.update(frame,im,read_dir)
        self.post_process()

    def post_process(self):
        for t in self.track_list:
            t.export()
            print 'track range ',t.frame_range,',', len(t.rec), ' rec available'

    def save_hdf5(self,filename):
        """saves all track data to HDF5 file
        """
        fid = h5py.File(filename, 'w')

        # create one experiment summary dataset
        n_track = len(self.track_list)

        summary = fid.create_group("summary")

        frames = summary.create_dataset('frames', (n_track,3), dtype=int)
        frames.attrs.create('labels',['#frame','first_frame','last_frame'])
        for no,t in enumerate(self.track_list):
            frames[no,:] = [len(t.rec),t.frame_range[0],t.frame_range[1]]

        # Tracks group
        tracks = fid.create_group("tracks")

        for no,t in enumerate(self.track_list):
            #one dataset per track
            track = tracks.create_group('track%04d'%no)
            track.attrs.create('frame_range',t.frame_range)
            print str(t.params)

            track.attrs.create('model',str(t.model))
            track.attrs.create('parameters',str(t.params))
            center = track.create_dataset('center', (t.data_center.shape[0],3), dtype=float)
            center.attrs.create('labels',['frame','x','y'])

            #first column contains the frames where the cell has been tracked
            frames = npy.arange(t.frame_range[0],t.frame_range[1])[:,npy.newaxis]
            center[:,:]= npy.hstack((frames,t.data_center))

            #one halo data per track
            halo = track.create_dataset('halo', t.data_halo.shape, dtype=float)
            halo[:,:,:] = t.data_halo
            halo.attrs.create('features',meanshift_features)
            halo.attrs.create('dims',['0-frame','1-pie#','2-features'])
            halo.attrs.create('frame_range',t.frame_range)

            #one soma data per track
            soma = track.create_dataset('soma', t.data_soma.shape, dtype=float)
            soma[:,:,:] = t.data_soma
            soma.attrs.create('features',meanshift_features)
            soma.attrs.create('dims',['0-frame','1-pie#','2-features'])
            soma.attrs.create('frame_range',t.frame_range)



#=================================================================================================

def test_experiment():
    """Test function: create an Experiment object for a sequence, data are saved in HDF5 file
    """
    #define sequence source
    #    datazip_filename = '../test/data/seq0_extract.zip'
    datazip_filename = '../test/data/seq0.zip'
    reader = Reader(ZipSource(datazip_filename))

    experiment = Experiment(reader,exp_name='Test')

    #mark initial cell position (may be in the middle of the sequence
    cellLocations = [(221,184),(408,158),(529,367),(585,150),(290,125)]
    params = {'N':16,'radius_halo':20,'radius_soma':12,'exp_halo':10,'exp_soma':2,'niter':10,'alpha':.75}
    track_list = []
    for x0,y0 in cellLocations:
        t = Track(x0=x0,y0=y0, model=Cell, frame0=0,params=params)
        experiment.add_track(t)

    #process the tracking
    experiment.track('fwd',last_frame=200)

    #save data to file
    experiment.save_hdf5('../test/temp/test.hdf5')

def test_track():
    """Test function: track some cells in a small sequence, compile cell positions into a Track object, print x,y
    """
    #define sequence source

#    datazip = '../test/data/seq0_extract.zip'
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
        g = reader.generator(read_dir=read_dir,first_frame=0,last_frame=10)
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
        x = t.data_center[:frame,0]
        y = t.data_center[:frame,1]
        print x,y



if __name__ == "__main__":

#    test_experiment()
    test_track()
