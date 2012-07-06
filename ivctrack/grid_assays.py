# -*- coding: utf-8 -*-
'''This file contains various assays on an image
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

from traits.api import HasTraits, Instance, Int, Dict, Class, Range, DelegatesTo, CArray, Button, Trait, Float
from traitsui.api import View, Group, Item, RangeEditor,ValueEditor,TableEditor,CustomEditor,TreeEditor,CompoundEditor
from enable.component_editor import ComponentEditor
from chaco.api import Plot, ArrayPlotData, jet, gray

from chaco.plot_graphics_context import PlotGraphicsContext

import numpy as npy

from chaco.tools.api import PanTool, ZoomTool

from ivctrack.cellmodel import Cell
from ivctrack.reader import ZipSource,Reader

from enable.api import BaseTool
import matplotlib.pyplot as plt


def get_marks(bg):
    """open an interactive plot and wait for cell marks
    """
    fig = plt.figure()
    plt.imshow(bg)
    xy = plt.ginput(n=0)
    plt.close(fig)
    return xy

def plot_grid(bg,model,params):
    """seach the convergence point for a grid af initial starting points
    plots the results (MPL)
    """
    print 'random seed'
    m,n = bg.shape
    N = 10
    xx,yy = npy.meshgrid(npy.linspace(0,n,N),npy.linspace(0,m,N))
    data = []
    for xr,yr in zip(xx.flatten(),yy.flatten()):
        print xr,yr
        cell = model(xr,yr,**params)
        cell.update(bg)
        data.append((xr,yr,cell.center[0],cell.center[1]))
    data = npy.asarray(data)
    print data

    plt.imshow(bg)
#    plt.plot(data[:,0],data[:,1],'or')
    plt.plot(data[:,2],data[:,3],'o')
    plt.show()

def plot_grid_path(bg,model,params):
    """seach the convergence point for a grid af initial starting points
    plots the results (MPL)
    """
    print 'random seed'
    m,n = bg.shape
    N = 5
    xx,yy = npy.meshgrid(npy.linspace(0,n,N),npy.linspace(0,m,N))
    data = []

    plt.figure()
    plt.imshow(bg)

    for xr,yr in zip(xx.flatten(),yy.flatten()):
        print xr,yr
        cell = model(xr,yr,**params)
        cell.update(bg)
        data.append((xr,yr,cell.center[0],cell.center[1]))
        plt.plot(cell.path[:,0],cell.path[:,1])
    data = npy.asarray(data)
    print data


    plt.show()

def preproc(bg):
    """test low level image filter
    """

    #special dependencies
    from pyrankfilter import rankfilter,__version__

    print __version__

    #custom structuring element
    xx,yy = npy.meshgrid(npy.linspace(-50,50,100),npy.linspace(-50,50,100))
    zz = npy.sqrt(xx**2+yy**2)

    struct_elem = npy.logical_and(zz>10,zz<20)

    plt.figure()
    f = rankfilter(bg,'median',struct_elem=struct_elem.astype('uint8'))
    plt.imshow(f)
    plt.show()

def preproc_dog(bg):
    """test low level image filter
    """

    #special dependencies
    from scipy.ndimage import gaussian_filter
    from pyrankfilter import rankfilter,__version__

    bg = bg.astype(float)
    f1 = gaussian_filter(bg,sigma=14.5)
    f2 = gaussian_filter(bg,sigma=15)

    f = ((f1-f2+3)*10).astype('uint8')

    loc_max = rankfilter(f,'highest',20,infSup=[0,0])

    r = bg.copy()
    r[loc_max>0]=0

    plt.figure()
    plt.subplot(2,2,1)
    plt.imshow(bg)
    plt.subplot(2,2,2)
    plt.imshow(f)
    plt.colorbar()
    plt.subplot(2,2,3)
    plt.imshow(loc_max)
    plt.subplot(2,2,4)
    plt.imshow(r)
    plt.show()

if __name__ == "__main__":

    datazip_filename = '../test/data/seq0_extract.zip'
    reader = Reader(ZipSource(datazip_filename))

    params = {'N':8,'radius_halo':22,'radius_soma':12,'exp_halo':20,'exp_soma':2,'niter':10,'alpha':.75}

#    plot_grid(reader.getframe(),model=Cell,params=params)
    preproc_dog(reader.moveto(29))
