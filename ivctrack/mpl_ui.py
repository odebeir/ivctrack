# -*- coding: utf-8 -*-
'''
Track cells using

* Meanshift

* Integral shift (todo)

'''
__author__ = 'Olivier Debeir'

import os
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
import numpy as npy
from scipy.misc import imread

from ivctrack.meanshift import LUT,generate_triangles,generate_inverted_triangles,meanshift,meanshift_features
from ivctrack.reader import ZipSource,Reader
from ivctrack.helpers import make_movie,timeit

from time import sleep
import h5py

class CellUi(object):
    """object responsible for the drawing of a Cell using Matplotlib
    """
    def __init__(self,cell,ax):
        self.cell = cell
        self.h=[]
        #create an interactive polygon

    def draw_triangles(self,ax):
        """Draws all the triangle in the given Matplotlib axis (ax)
        """
        idxx = [0,2,4,0]
        idxy = [1,3,5,1]
        for tri in self.cell.tri_soma:
            self.h.append(ax.plot(npy.take(tri,idxx),npy.take(tri,idxy),color = [.5,.5,.5]))
        for tri in self.cell.tri_halo:
            self.h.append(ax.plot(tri[0:6:2],tri[1:6:2],color = [.5,.5,.5]))

    def draw_centroids(self,ax):
        """Draws all the centroids in the given Matplotlib axis (ax)
        """
        for sh in self.cell.shift_halo:
            r = plt.Rectangle((sh[0]-1,sh[1]-1),3,3, facecolor=[.8,.8,.8])
            self.h.append(ax.add_artist(r))
        for sh in self.cell.shift_soma:
            r = plt.Rectangle((sh[0]-1,sh[1]-1),3,3, facecolor=[.1,.1,.1])
            self.h.append(ax.add_artist(r))

    def draw(self,ax):
        if len(self.h):
            for h in list(self.h):
                print h,type(h)
                if type(h) == type([]):
                    for hh in list(h):
                        print 'remove',hh
                        hh.remove()
                else:
                    print 'remove',h
#                    h.remove()

        r = plt.Rectangle((self.cell.center[0]-1,self.cell.center[1]-1),3,3, facecolor=[.5,.5,.1])
        self.h.append(ax.add_artist(r))
        self.draw_triangles(ax)
        self.draw_centroids(ax)


from matplotlib.artist import Artist
from matplotlib.patches import Polygon, CirclePolygon
from numpy import sqrt, nonzero, equal, array, asarray, dot, amin, cos, sin
from matplotlib.mlab import dist_point_to_segment
from pylab import *

class PolygonInteractor:
    """
    An polygon editor.

    Key-bindings

      't' toggle vertex markers on and off.  When vertex markers are on,
          you can move them, delete them

      'd' delete the vertex under point

      'i' insert a vertex at point.  You must be within epsilon of the
          line connecting two existing vertices

    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, ax, poly):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x,y,marker='o', markerfacecolor='r', animated=True)
        self.ax.add_line(self.line)
        #self._update_line(poly)

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None # the active vert

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas


    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state


    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = nonzero(equal(d, amin(d)))[0]
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None

        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts: return
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts: return
        if event.button != 1: return
        self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='t':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts: self._ind = None
        elif event.key=='d':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                self.poly.xy = [tup for i,tup in enumerate(self.poly.xy) if i!=ind]
                self.line.set_data(zip(*self.poly.xy))
        elif event.key=='i':
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y # display coords
            for i in range(len(xys)-1):
                s0 = xys[i]
                s1 = xys[i+1]
                d = dist_point_to_segment(p, s0, s1)
                if d<=self.epsilon:
                    self.poly.xy = array(
                        list(self.poly.xy[:i]) +
                        [(event.xdata, event.ydata)] +
                        list(self.poly.xy[i:]))
                    self.line.set_data(zip(*self.poly.xy))
                    break


        self.canvas.draw()

    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

def test_polygon(ax):
    from pylab import Polygon

    theta = arange(0, 2*pi, 0.4)
    r = 30

    xs = r*cos(theta)
    ys = r*sin(theta)

    poly = Polygon(zip(100+xs, 100+ys,), animated=True)
    ax.add_patch(poly)
    p = PolygonInteractor( ax, poly)

    return p

if __name__ == "__main__":
    from pylab import *

    fig = figure()
    theta = arange(0, 2*pi, 0.1)
    r = 1.5

    xs = r*cos(theta)
    ys = r*sin(theta)

    poly = Polygon(zip(xs, ys,), animated=True)
    ax = subplot(111)
    ax.add_patch(poly)
    p = PolygonInteractor( ax, poly)

    #ax.add_line(p.line)
    ax.set_title('Click and drag a point to move it')
    ax.set_xlim((-2,2))
    ax.set_ylim((-2,2))
    show()