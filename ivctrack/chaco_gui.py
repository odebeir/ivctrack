# -*- coding: utf-8 -*-
'''This file contains one attempt to display model with Chaco framework
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

from traits.api import HasTraits, Instance, Int, Dict, Class, Range, DelegatesTo, CArray, Button
from traitsui.api import View, Group, Item, RangeEditor
from enable.component_editor import ComponentEditor
from chaco.api import Plot, ArrayPlotData

from chaco.plot_graphics_context import PlotGraphicsContext

import numpy as npy

from chaco.tools.api import PanTool, ZoomTool

from ivctrack.cellmodel import Cell
from ivctrack.reader import ZipSource,Reader

from enable.api import BaseTool

def save_plot(plot, filename, width, height):
    plot.outer_bounds = [width, height]
    plot.do_layout(force=True)
    gc = PlotGraphicsContext((width, height), dpi=72)
    gc.render_component(plot)
    gc.save(filename)

class CustomTool(BaseTool):
    current_position = CArray()
    def normal_right_down(self, event):
        """see http://code.enthought.com/projects/files/ets_api/enthought.enable.events.MouseEvent.html
        """
        #map to the data coordinate
        data = self.component.map_data((event.x, event.y))
        self.current_position = data

class ScatterPlotTraits(HasTraits):

    button = Button('Print')
    reader = Instance(Reader)

    frame = Range(low = 0)
    low = Int(0)
    high = Int(1)

    model = Class(Cell)
    params = Dict()

    x0 = Range(0,640.,200)
    y0 = Range(0,640.,200)

    cell = Instance(Cell)

    plot = Instance(Plot)

    cursor1 = Instance(CustomTool)
    cursor1pos = DelegatesTo('cursor1', prefix='current_position')

    traits_view = View(
        Group(Item('button', show_label=False),
            Item('plot', editor=ComponentEditor(), show_label=False),
            Item('params',   show_label=False),
            Item('x0',  show_label=False),
            Item('y0',  show_label=False),
            Item('frame', editor = RangeEditor(mode = 'slider',low_name='low',high_name='high'),   show_label=False),
            orientation = "vertical"),
        width=800, height=600, resizable=True, title="Chaco Plot")

    def __init__(self,reader,model,params):
        super(ScatterPlotTraits, self).__init__()

        self.reader = reader
        self.high = self.reader.N()-1
        self.model = model #class not an instance (needed to rebuild a nex instance when parameters are change)
        self.params = params

        x = npy.linspace(-6.28, 6.28, 100)
        y = npy.sin(x)

        self.plotdata = ArrayPlotData(x = x, y = y , imagedata = self.reader.getframe(),x0=[self.x0],y0=[self.y0],
                                        xc=[self.x0],yc=[self.y0])

        plot = Plot(self.plotdata)
        plot.img_plot("imagedata") #, colormap=jet
        plot.plot(("x0", "y0"), type="scatter", color="red")
        plot.plot(("xc", "yc"), type="scatter", color="yellow")
        plot.plot(("x", "y"), type="line", color="blue")
        self.renderer = plot.plot(("x", "y"), type="scatter", color="blue")[0]

        self.plot = plot

        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))

        self.cursor1 = CustomTool(plot)
        plot.tools.append(self.cursor1)
        self.cell_update()

    def _params_changed(self):
        """when cell parameters are changed, a new cell replace the previous one
        """
        print self.params
        self.cell = self.model(225,180,**self.params)
        self.cell.set(self.x0,self.y0)
        self.cell_update()

    def _frame_changed(self):
        self.plotdata.set_data('imagedata', self.reader.moveto(self.frame))
        self.cell_update()

    def cell_update(self):
        self.cell.update(self.reader.getframe())
        halo = npy.asarray([sh[0:2] for sh in self.cell.shift_halo])
        try:
            self.plotdata.set_data('x', halo[:,0])
            self.plotdata.set_data('y', halo[:,1])
            self.plotdata.set_data('xc', [self.cell.x])
            self.plotdata.set_data('yc', [self.cell.y])

        except AttributeError:
            pass #skip if plotdata not yet initialized

    def _x0_changed(self):
        self.cell.set(self.x0,self.y0)
        self.plotdata.set_data('x0', [self.x0])
        self.plotdata.set_data('y0', [self.y0])
        self.cell_update()

    def _y0_changed(self):
        self.cell.set(self.x0,self.y0)
        self.plotdata.set_data('x0', [self.x0])
        self.plotdata.set_data('y0', [self.y0])
        self.cell_update()

    def _cursor1pos_changed(self):
        self.x0,self.y0 = self.cursor1pos
        self.cell_update()

    def _button_fired(self):
        print 'hop'
        save_plot(self.plot,'fig.png',1028,768)

if __name__ == "__main__":

    datazip_filename = '../test/data/seq0_extract.zip'
    reader = Reader(ZipSource(datazip_filename))

    params = {'N':8,'radius_halo':20,'radius_soma':12,'exp_halo':10,'exp_soma':2,'niter':10,'alpha':.75}

    demo = ScatterPlotTraits(reader=reader,params=params,model=Cell)

    demo.configure_traits()