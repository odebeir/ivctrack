from traits.api import HasTraits, Instance, Int, Dict, Class, Range, DelegatesTo, CArray
from traitsui.api import View, Group, Item, TextEditor,RangeEditor,ValueEditor,ListEditor
from enable.api import ColorTrait
from enable.component_editor import ComponentEditor
from chaco.api import marker_trait, Plot, ArrayPlotData
from chaco.tools.cursor_tool import CursorTool, BaseCursorTool

from numpy import linspace, sin,meshgrid,exp
import numpy as npy

from chaco.tools.api import PanTool, ZoomTool, DragZoom, DragTool


from ivctrack.cellmodel import Cell
from ivctrack.reader import ZipSource,Reader


from enable.api import BaseTool

class CustomTool(BaseTool):
    current_position = CArray()
    def normal_right_down(self, event):
        """see http://code.enthought.com/projects/files/ets_api/enthought.enable.events.MouseEvent.html
        """
        #map to the data coordinate
        data = self.component.map_data((event.x, event.y))
        self.current_position = data

class ScatterPlotTraits(HasTraits):

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
        Group(
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

        x = linspace(-6.28, 6.28, 100)
        y = sin(x)

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

if __name__ == "__main__":

    datazip_filename = '../test/data/seq0_extract.zip'
    reader = Reader(ZipSource(datazip_filename))

    params = {'N':8,'radius_halo':20,'radius_soma':12,'exp_halo':10,'exp_soma':2,'niter':10,'alpha':.75}

    demo = ScatterPlotTraits(reader=reader,params=params,model=Cell)

    demo.configure_traits()