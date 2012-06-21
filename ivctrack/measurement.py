# -*- coding: utf-8 -*-
'''Trajectory feature extraction
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
import numpy as npy
from hdf5_read import get_hdf5_data
from quickhull2d import qhull
from scipy.spatial.distance import pdist,squareform

def inst_speed(xy):
    s = npy.sqrt(npy.sum(npy.diff(xy,axis=0)**2,axis=1))
    return s

def path_length(xy):
    return npy.sum(inst_speed(xy))

def avg_speed(xy):
    return path_length(xy)/xy.shape[0]

def mrdo_speed(xy):
    xy0 = xy[0,:]
    d = npy.sqrt(npy.sum((xy-xy0)**2,axis=1))
    d_max = npy.max(d)
    return d_max/xy.shape[0]

def hull_speed(xy):
    hull_xy = qhull(xy)
    d = pdist(hull_xy, 'euclidean')
    dmax_idx = npy.argmax(d)
    return d[dmax_idx]/xy.shape[0]

def plot_hull_speed(xy):
    import matplotlib.pyplot as plt

    hull_xy = qhull(xy)
    d = pdist(hull_xy, 'euclidean')
    dmax_idx = npy.argmax(d)

    r = npy.zeros_like(d)
    r[dmax_idx] = 1
    sd = squareform(r)

    ext_idx = npy.nonzero(sd)[1]
    p0 = hull_xy[ext_idx[0],:]
    p1 = hull_xy[ext_idx[1],:]

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    plt.scatter(xy[:,0],xy[:,1])
    plt.plot(hull_xy[:,0],hull_xy[:,1])
    plt.plot([p0[0],p1[0]],[p0[1],p1[1]])
    plt.show()
    return 0

def speed_feature_extraction(hdf5_filename):

    features,data = get_hdf5_data(hdf5_filename,fields=['center'])
    measures = []
    feat_name = ['path_length','avg_speed','mrdo','hull_speed']
    for d in data:
        xy = d['center']
        pl = path_length(xy)
        avg = avg_speed(xy)
        mrdo = mrdo_speed(xy)
        h = hull_speed(xy)
        measures.append((pl,avg,mrdo,h))
    measures = npy.asarray(measures)

    return (feat_name,measures)

if __name__=='__main__':

    import matplotlib.pyplot as plt

    hdf5_filename = '../test/data/test_rev.hdf5'

    feat,data = speed_feature_extraction(hdf5_filename)
    print feat
    print data

    plt.scatter(data[:,1],data[:,3])
    plt.show()