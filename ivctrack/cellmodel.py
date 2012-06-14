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

from datetime import datetime
from time import sleep
import csv
import h5py

class Cell():
    """Cell object, the model is described by:

    * a cell position

    * the number of division (for both outer and inner part)

    * the weight Look Up Table used for the inner (black soma) and for the outer part (white halo)
    """
    def __init__(self,x0,y0,N=16,radius_halo=30,radius_soma=12,exp_halo=10,exp_soma=2,niter=10,alpha=.75):
        #model center
        self.center = npy.asarray((x0,y0))

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
        self.tri_halo = generate_triangles(self.center[0],self.center[1],self.N,self.radius_halo)
        self.tri_soma = generate_inverted_triangles(self.center[0],self.center[1],self.N,self.radius_soma)

    def set(self,x,y):
        self.center[0] = x
        self.center[1] = y
        self.build_triangles()

    def update(self,im):
        """Update cell position with respect to a given image
        """
        self.path = npy.zeros((self.niter,2))
        for iter in range(self.niter):
            #compute the shifts
            self.shift_halo = meanshift(im,self.tri_halo,0.0,0.0,lut = self.LutW)
            self.shift_soma = meanshift(im,self.tri_soma,0.0,0.0,lut = self.LutB)

            #update the position
            # halo centroid
            halo = npy.asarray([sh[0:2] for sh in self.shift_halo])
            # nucleus centroid
            soma = npy.asarray([sh[0:2] for sh in self.shift_halo])

            self.center[:] = (1.-self.alpha) * soma.mean(axis=0) + self.alpha * halo.mean(axis=0)
            self.path[iter,:] = self.center

            #update the triangles
            self.build_triangles()

    def rec(self):
        """returns a record grouping cell useful data
        """
        return (self.center.copy(),self.shift_halo.copy(),self.shift_soma.copy())

    def rec_structure(self):
        """returns the structure of a rec produced by this model
        one dict entry will generate a distinct dataset, each line of these datasets will be populated with model data
        """
        center = {'dataset_name':'center',
                  'attributes':[('features',['x','y']),]}
        halo = {'dataset_name':'halo',
                'attributes':[('features',meanshift_features),('dims',['0-frame','1-pie#','2-features'])]}
        soma = {'dataset_name':'soma',
                'attributes':[('features',meanshift_features),('dims',['0-frame','1-pie#','2-features'])]}

        return [center,halo,soma]

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
        self.records = {}                           # data record

    def reset_cell_pos(self):
        self.frame = self.frame0
        self.cell.set(self.x0,self.y0)

    def update(self,frame,im,dir):
        if dir=='fwd':
            if (frame == self.frame+1) | (frame == self.frame):
                self.cell.update(im)
                self.records[frame] = self.cell.rec()
                self.frame = frame
                self.frame_range[1] = self.frame

        if dir=='rev':
            if (frame == self.frame-1) | (frame == self.frame):
                self.cell.update(im)
                self.records[frame] = self.cell.rec()
                self.frame = frame
                self.frame_range[0] = self.frame


    def export_to_hdf5(self,hdf5_group):
        """write the track results into the given HDF5 group
        """
        hdf5_group.attrs.create('frame_range',self.frame_range)

        hdf5_group.attrs.create('model',str(self.model))
        hdf5_group.attrs.create('parameters',str(self.params))

        # specific track data (depends on cell model)
        L = list(self.records)
        L.sort()
        for i,s in enumerate(self.cell.rec_structure()):
            #extract data
            data = []
            for k in L:
                data.append(self.records[k][i])
            #create dataset
            data = npy.asarray(data)
            ds = hdf5_group.create_dataset(s['dataset_name'], data.shape, dtype=float)
            ds[:,:] = data
            #add attributes to the dataset
            for att_name,att_list in s['attributes']:
                ds.attrs.create(att_name,att_list)

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

    def do_tracking(self,read_dir,first_frame=0,last_frame=None):
        r  = range(0,self.reader.N())
        frames = list(r[first_frame:last_frame])

        #reset Cell to mark position before changing tracking direction
        for t in self.track_list:
            t.reset_cell_pos()
        if read_dir=='fwd':
            for frame in frames:
                print 'process frame ',frame
                im = self.reader.moveto(frame)
                for t in self.track_list:
                    t.update(frame,im,read_dir)
        if read_dir=='rev':
            frames.reverse()
            for frame in frames:
                print 'process frame ',frame
                im = self.reader.moveto(frame)
                for t in self.track_list:
                    t.update(frame,im,read_dir)

    def save_hdf5(self,filename):
        """saves all track data to HDF5 file
        """
        fid = h5py.File(filename, 'w')

        # create one experiment SUMMARY dataset
        # these data are common for all models
        n_track = len(self.track_list)
        summary = fid.create_group("summary")
        summary.attrs.create('seq.source',[str(self.reader.source),self.reader.source.description])
        # valid frames
        frames = summary.create_dataset('frames', (n_track,3), dtype=int)
        frames.attrs.create('features',['#frame','first_frame','last_frame'])
        for no,t in enumerate(self.track_list):
            frames[no,:] = [len(t.records),t.frame_range[0],t.frame_range[1]]
        # marks
        marks = summary.create_dataset('marks', (n_track,3), dtype=int)
        marks.attrs.create('features',['x','y','#frame'])
        for no,t in enumerate(self.track_list):
            marks[no,:] = [t.x0,t.y0,t.frame0]

        # TRACK group
        tracks = fid.create_group("tracks")
        export_datetime = datetime.now().isoformat(' ')
        tracks.attrs.create('date',[export_datetime])
        for no,t in enumerate(self.track_list):
            # one group per track
            track = tracks.create_group('track%04d'%no)
            t.export_to_hdf5(track)

#=================================================================================================
def import_marks(filename):
    """read a CSV file containing lines such as:
    x,y,frame
    for each cell to be tracked
    """
    csvreader = csv.reader(open(filename, 'rb'), delimiter=',')
    marks = []
    for row in csvreader:
        marks.append((float(row[0]),float(row[1]),float(row[2])))
    return npy.asarray(marks)

def test_experiment():
    """Test function: create an Experiment object for a sequence, data are saved in HDF5 file
    """
    #define sequence source
    datazip_filename = '../test/data/seq0_extract.zip'
#    datazip_filename = '../test/data/seq0.zip'
    reader = Reader(ZipSource(datazip_filename))

    experiment = Experiment(reader,exp_name='Test')

    #mark initial cell position (may be in the middle of the sequence
    marks = import_marks('../test/data/fwd_marks.csv')
    params = {'N':8,'radius_halo':20,'radius_soma':12,'exp_halo':10,'exp_soma':2,'niter':10,'alpha':.75}

    track_list = []
    for x0,y0,frame0 in marks:
        t = Track(x0=x0,y0=y0,frame0=frame0,model=Cell,params=params)
        experiment.add_track(t)

    #process the tracking
    experiment.do_tracking('rev')
    experiment.do_tracking('fwd')

    #save data to file
    experiment.save_hdf5('../test/temp/test.hdf5')

def test_track():
    """Test function: track some cells in a small sequence, compile cell positions into a Track object, print x,y
    """
    #define sequence source

    datazip = '../test/data/seq0_extract.zip'
#    datazip = '../test/data/seq0.zip'
    reader = ZipSource(datazip)

    #mark initial cell position (may be in the middle of the sequence
    #from first frame fwd
    cellLocations = [(221,184),(408,158),(529,367)]

    params = {'N':16,'radius_halo':30,'radius_soma':15}
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

#    #post process the records
#    for t in track_list:
#        t.export()
#        print 'track range ',t.frame_range,',', len(t.rec), ' rec available'
#        x = t.data_center[:frame,0]
#        y = t.data_center[:frame,1]
#        print x,y
#...to be fixed




if __name__ == "__main__":

#    test_experiment()
    test_track()
