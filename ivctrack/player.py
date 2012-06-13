# -*- coding: utf-8 -*-
'''GUI for interactive sequence manipulation using Matplotlib
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
from MPLeditor import MPLFigureEditor

import os.path as path
import re
import matplotlib.pyplot as plt
import numpy as npy

from helpers import timeit

from ivctrack.reader import ZipSource,Reader,DumbSource
from ivctrack.cellmodel import Cell
from ivctrack.mpl_ui import CellUi,test_polygon

import h5py

import wx
from matplotlib.figure import Figure

from enthought.traits.api import Any,Instance,Range,Float,Int,Button,Bool,String,Dict,List
from enthought.traits.api import HasTraits
from enthought.traits.ui.api import View,Item,VGroup,HGroup,RangeEditor,InstanceEditor,TextEditor,ListEditor
from enthought.traits.ui.api import Tabbed, HSplit, VSplit, spring
from enthought.traits.ui.wx.themed_slider_editor import ThemedSliderEditor

from threading import Thread
from time import sleep
from pyface.timer.api import Timer


class FirstFrame(object):
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
        im = self.reader.rewind()
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

class Tracker(HasTraits):
    name = String('no name')
    N = Int(16)
    radius_halo = Float(30)
    radius_soma = Float(15)
    exp_halo = Float(10)
    exp_soma = Float(2)
    alpha = Float(.75)
    niter = Int(2)

    traits_view = View(VGroup(
                    Item('name',  show_label=True),
                    Item('N', show_label=True),
                    Item('radius_halo', show_label=True),
                    Item('radius_soma', show_label=True),
                    Item('exp_halo', show_label=True),
                    Item('exp_soma', show_label=True),
                    Item('alpha', show_label=True),
                    Item('niter', show_label=True),
                )
            )
    def __init__(self):
        self.model = Cell(0,0)
        self.ui = CellUi(self.model)

    def draw(self,ax):
        self.ui.draw(ax)

class InteractivePlayer(HasTraits):

    #data info
    source = String()
    data = String()
    model = String()
    params = String()

    #tracker
    #todo

    figure = Instance(Figure, ())
    #Frame selection
    frame = Range(low = 0)
    fwd = Bool(False)
    rev = Bool(False)
    low = Int(0)
    high = Int(1)
    timer = Instance(Timer)

    view = View(HSplit(
            VGroup(
                Item('figure', editor=MPLFigureEditor(),show_label=False,width=600),
                HGroup(
                    Item('rev',  show_label=True),
                    Item('fwd',  show_label=True),
                    Item('frame', editor = RangeEditor(mode = 'slider',low_name='low',high_name='high') ,
                        show_label=False,width=400),
                    Item('frame', editor = RangeEditor(mode = 'spinner',low_name='low',high_name='high') ,),
                ),
            ),
            VSplit(
                Tabbed(
                    VGroup(
                        label='Model',
                    ),
                    VGroup(
                        Item('source',  show_label=True,resizable=False,style='readonly'),
                        Item('data',  show_label=True,resizable=False,style='readonly'),
                        '_',
                        Item('model',  show_label=True,resizable=False,style='readonly'),
                        Item('params',  show_label=True,resizable=False,style='custom',editor=TextEditor()),
                        label='Info',

                    ),
                ),
                Tabbed(
                    VGroup(
#                        Item('rev',  show_label=True,resizable=True),
                        label='Display',
                    ),
                    VGroup(
#                        Item('rev',  show_label=True,resizable=True),
                        label='Tools',
                    )
                ),
            ),
        ),
        width=1000,
        height=600,
        resizable=True
        )

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(10, self.onTimer)
        return super(InteractivePlayer, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(10, self.onTimer)
        return super(InteractivePlayer, self).configure_traits(*args, **kws)

    def onTimer(self):
        if self.fwd:
            if self.frame<self.reader.N()-1:
                self.frame += 1
            else:
                self.fwd = False
        if self.rev:
            if self.frame>0:
                self.frame -= 1
            else:
                self.rev = False

    def _figure_default(self):
        figure = Figure()
        figure.add_axes([0,0,1,1])

        return figure

    def __init__(self,reader,hdf5filename):
        super(InteractivePlayer, self).__init__()
        #init data
        self.reader = reader
        self.source = self.reader.source.description
        self.hdf5filename = hdf5filename
        if hdf5filename is None:
            self.fid = None
            self.data = 'no data'
            self.model = 'no model'
            self.params = ''
        else:
            self.fid = h5py.File(hdf5filename, 'r')
            self.data = hdf5filename
            t0 = list(self.fid['tracks'])[0]
            self.model = str(self.fid['tracks'][t0].attrs['model'])
            self.params = str(self.fid['tracks'][t0].attrs['parameters'])
        self.low = 0
        self.high = self.reader.N()-1

        self.p = None


    def update_bg(self):
        if self.p is None:
            self.p = test_polygon(self.figure.axes[0])
        im = self.reader.getframe()
        self.figure.axes[0]
        self.figure.axes[0].images=[]
        self.figure.axes[0].imshow(im,interpolation='none')

    def update(self):
        self.update_bg()
        if self.fid is not None:
            self.update_overlay()
        wx.CallAfter(self.figure.canvas.draw)

    def update_overlay(self):
        self.figure.axes[0].lines=[]
        tracks = self.fid['tracks']
        for t in tracks:
            first,last = tracks[t].attrs['frame_range']
            if self.frame < first:
                #fade
                xy= tracks[t]['halo'][0,:,0:2]
                self.figure.axes[0].plot(xy[:,0],xy[:,1],'wo',alpha=.5)
            elif self.frame> last:
                #fade
                xy= tracks[t]['halo'][-1,:,0:2]
                self.figure.axes[0].plot(xy[:,0],xy[:,1],'wo',alpha=.5)
            else:
                #valid position
                xy= tracks[t]['halo'][self.frame-first,:,0:2]
                self.figure.axes[0].plot(xy[:,0],xy[:,1],'ro')
                xy= tracks[t]['soma'][self.frame-first,:,0:2]
                self.figure.axes[0].plot(xy[:,0],xy[:,1],'bo')

    def _fwd_fired(self):
        if self.fwd:
            self.rev = False

    def _rev_fired(self):
        if self.rev:
            self.fwd = False

    def _frame_changed(self):
        self.reader.moveto(self.frame)
        self.update()

#=================================================================================================
def test_player():
    """reopen an HDF5 file
    """
    datazip_filename = '../test/data/seq0_extract.zip'
    hdf5filename = '../test/temp/test.hdf5'

    reader = Reader(ZipSource(datazip_filename))
#    reader = Reader(DumbSource())
#    player = FirstFrame(reader,hdf5filename)

    player = InteractivePlayer(reader,hdf5filename)

    player.configure_traits()


if __name__=='__main__':

    test_player()