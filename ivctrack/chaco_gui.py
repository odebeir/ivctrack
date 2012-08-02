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

from traits.api import HasTraits, Instance, Int, Dict, Class, Range, DelegatesTo, CArray, Button, Trait, Float, Enum, Bool
from traitsui.api import RangeEditor,ValueEditor,TableEditor,CustomEditor,TreeEditor,CompoundEditor,EnumEditor
from traitsui.api import HGroup,VGroup,View,Group, Item
from enable.component_editor import ComponentEditor
from chaco.api import Plot, ArrayPlotData, jet, gray
from chaco.plot_graphics_context import PlotGraphicsContext

import numpy as npy

from chaco.tools.api import PanTool, ZoomTool

from cellmodel import Cell,AdaptiveCell
from reader import ZipSource,Reader

from enable.api import BaseTool

from pyface.timer.api import Timer

from grid_assays import plot_grid,get_marks


class AutoParam(HasTraits):
    """create a parameters structure from a Dict
    """
    def __init__(self, **traits):
        HasTraits.__init__(self,**traits)
    def set(self,params):
        for k in params:
            self.__setattr__(k,params[k])
            self.add_trait(k,type(params[k]))
    def get_dict(self):
        """returns the updated dict
        """
        return self.__dict__


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

    paramsUI = Instance(AutoParam)

    button = Button('Print')
    create_marks = Button('create marks')
    export_model = Button('export model')

    fwd = Bool(False)
    rev = Bool(False)
    timer = Instance(Timer)

    reader = Instance(Reader)

    frame = Range(low = 0)
    low = Int(0)
    high = Int(1)

    model = Enum(Cell,AdaptiveCell)
    params = Dict()

    x0 = Float(100)
    y0 = Float(100)

    cell = Instance(Cell)

    plot = Instance(Plot)

    cursor1 = Instance(CustomTool)
    cursor1pos = DelegatesTo('cursor1', prefix='current_position')

    traits_view = View(
        HGroup(VGroup(
            Item(name='model',
                editor=EnumEditor(values={
                    Cell : '1:Cell',
                    AdaptiveCell    : '2:AdaptiveCell',
                    }
                )
            ),
            Item('export_model', show_label=False),
            Item('paramsUI',style='custom', show_label=False),
            Item('frame', editor = RangeEditor(mode = 'slider',low_name='low',high_name='high'),   show_label=False),
            HGroup(Item('rev'),Item('fwd')),
            ),
            VGroup(Item('button', show_label=False),
            Item('create_marks', show_label=False),
            Item('plot', editor=ComponentEditor(), show_label=False),
            orientation = "vertical"),
            ),
        width=800, height=600, resizable=True, title="Chaco Plot")

    def __init__(self,reader,model,params):
        super(ScatterPlotTraits, self).__init__()

        #data
        self.reader = reader
        self.high = self.reader.N()-1
        self.model = model #class not an instance (needed to rebuild a nex instance when parameters are change)
        self.params = params

        #parameters panel
        self.paramsUI = AutoParam()
        self.paramsUI.set(params)
        self.paramsUI.on_trait_event(self.update_param)

        self.plotdata = ArrayPlotData(xh=npy.zeros((1,)),yh=npy.zeros((1,)),
                                    xs=npy.zeros((1,)),ys=npy.zeros((1,)),
                                    imagedata=self.reader.getframe(),
                                    x0=[self.x0],y0=[self.y0],
                                    xc=[self.x0],yc=[self.y0],
                                    x_path=[self.x0],y_path=[self.y0])

        plot = Plot(self.plotdata)
        plot.img_plot("imagedata",colormap=gray) #, colormap=jet
        plot.plot(("x0", "y0"), type="scatter", color="red",marker='triangle')
        plot.plot(("xc", "yc"), type="scatter", color="yellow")
        plot.plot(("x_path", "y_path"), type="line", color="green",marker='circle')
        plot.plot(("xh", "yh"), type="scatter", color="blue",marker='circle')
        plot.plot(("xs", "ys"), type="scatter", color="white",marker='circle',size=5)

        self.plot = plot

        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))

        self.cursor1 = CustomTool(plot)
        plot.tools.append(self.cursor1)
        self.cell_update()

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(5, self.onTimer)
        return super(ScatterPlotTraits, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(5, self.onTimer)
        return super(ScatterPlotTraits, self).configure_traits(*args, **kws)

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

    def update_param(self):
        self.params = self.paramsUI.get_dict()

    def _model_changed(self):
        self._params_changed()

    def _params_changed(self):
        """when cell parameters are changed, a new cell replace the previous one
        """
        self.cell = self.model(225,180,**self.params)
        self.cell.set(self.x0,self.y0)
        self.cell_update()

    def _frame_changed(self):
        self.plotdata.set_data('imagedata', self.reader.moveto(self.frame))
        self.cell_update()

    def _fwd_changed(self):
        if self.fwd:
            self.rev = False
    def _rev_changed(self):
        if self.rev:
            self.fwd = False


    def cell_update(self):
        self.cell.update(self.reader.getframe())
        halo = npy.asarray([sh[0:2] for sh in self.cell.shift_halo])
        soma = npy.asarray([sh[0:2] for sh in self.cell.shift_soma])
        try:
            self.plotdata.set_data('xh', halo[:,0])
            self.plotdata.set_data('yh', halo[:,1])
            self.plotdata.set_data('xs', soma[:,0])
            self.plotdata.set_data('ys', soma[:,1])
            self.plotdata.set_data('xc', [self.cell.center[0]])
            self.plotdata.set_data('yc', [self.cell.center[1]])
            self.plotdata.set_data('x_path', self.cell.path[:,0])
            self.plotdata.set_data('y_path', self.cell.path[:,1])
            self.plotdata.set_data('x0', [self.x0])
            self.plotdata.set_data('y0', [self.y0])

        except AttributeError:
            pass #skip if plotdata not yet initialized


    def _cursor1pos_changed(self):
        self.x0,self.y0 = self.cursor1pos
        self.cell.set(self.x0,self.y0)
        self.cell_update()

    def _button_fired(self):
        save_plot(self.plot,'../test/temp/fig.png',1028,768)

    def _export_model_fired(self):
        import json
        s = json.dumps(self.params)
        print s
        filename = 'parameters.json'
        fid = open(filename,'w+t')
        fid.write(s)
        del fid
        print 'parameters saved in ',filename

    def _create_marks_fired(self):
        """seach the convergence point for a grid af initial starting points
        plots the results (MPL)
        """
#        plot_grid(bg=self.reader.getframe(),model=self.model,params=self.params)
        t = self.reader.head
        xy = get_marks(bg=self.reader.getframe())
        print xy,t
        filename = 'marks.csv'
        fid = open(filename,'w+t')
        for x,y in xy:
            fid.write('%f,%f,%d\n'%(x,y,t))
        del fid
        print 'marks saved in ',filename

def test_gui(datazip_filename):
    reader = Reader(ZipSource(datazip_filename))
    params = {'N':16,'radius_halo':23,'radius_soma':12,'exp_halo':20,'exp_soma':2,'niter':10,'alpha':.75}
    demo = ScatterPlotTraits(reader=reader,params=params,model=AdaptiveCell)
    demo.configure_traits()


if __name__ == "__main__":


    datazip_filename = '../test/data/seq0.zip'
#    datazip_filename = '../test/data/seq0_extract.zip'
#    datazip_filename = '../test/data/u373s08127ct1.zip'

    reader = Reader(ZipSource(datazip_filename))

    params = {'N':16,'radius_halo':23,'radius_soma':12,'exp_halo':20,'exp_soma':2,'niter':10,'alpha':.75}

    demo = ScatterPlotTraits(reader=reader,params=params,model=AdaptiveCell)

    demo.configure_traits()