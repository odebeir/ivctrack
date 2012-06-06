# -*- coding: utf-8 -*-
'''Mean shift implementation using integral images to compute centroid on rectangles

.. note::

    integral images are computed using *skimage.transform.integral_image*

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

from skimage.transform import integral_image,integrate
import numpy as np

import matplotlib.pyplot as plt

import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from scipy.ndimage import imread

def test_image(s=0):
    t = np.zeros((100,120),dtype='uint8')
    if s==0:
        t[30:50,20:40] = 255
    if s==1:
        x,y = np.meshgrid(range(20,40),range(30,50))
        t[30:50,20:40] = x
    if s==2 :
        x,y = np.meshgrid(range(20,40),range(30,50))
        t[30:50,20:40] = 55 - np.sqrt((x-30)**2+(y-40)**2)
    if s==3:
        t = imread('../test/data/crop.jpg').astype(float)
        #normalization
        t = (t-t.min())/(t.max()-t.min())
        t = t**2
    if s==4:
        t = imread('../test/data/exp0001.jpg').astype(float)
        #normalization
        t = (t-t.min())/(t.max()-t.min())
        t = t**2
    return t

class IntegratedImage(object):
    """Object keeping the integral image and the X,Y integral images
    """
    def __init__(self,array):
        self.m,self.n = array.shape
        COL,ROW = np.meshgrid(range(0,self.n),range(0,self.m))

        self.mat = integral_image(array)
        self.r_mat = integral_image(ROW*array)
        self.c_mat = integral_image(COL*array)

    def valid_rectangle(self,rect):
        """return a valid rectangle w.r.t. image size
        """

        r1,r2 = (min(int(rect[0]),int(rect[2])),max(int(rect[0]),int(rect[2])))
        c1,c2 = (min(int(rect[1]),int(rect[3])),max(int(rect[1]),int(rect[3])))
        r1 = int(max(0,r1))
        r2 = int(min(self.m-1,max(r2,0)))
        c1 = int(max(0,c1))
        c2 = int(min(self.n-1,max(c2,0)))

        return (r1,c1,r2,c2)

    def get_sum(self,integral_image,rect):
        """returns sum inside rect
        """
        r1,c1,r2,c2 = self.valid_rectangle(rect)

        a = integral_image[r1,c1]
        b = integral_image[r1,c2]
        c = integral_image[r2,c2]
        d = integral_image[r2,c1]

        return c+a-b-d

    def surf_rect(self,rect):
        return (rect[2]-rect[0])*(rect[3]-rect[1])

    def get_value(self,r,c):
        return self.mat[r,c]
    
    def find_g(self,rect):
        """returns centroid of the rectangle
        """
        vrect = self.valid_rectangle(rect)

        sum = self.get_sum(self.mat,vrect)
        rsum = self.get_sum(self.r_mat,vrect)
        csum = self.get_sum(self.c_mat,vrect)

        if sum>0:
            rg = rsum/sum
            cg = csum/sum
            mean = sum/self.surf_rect(vrect)
        else:
            rg = (vrect[0]+vrect[2])/2.0
            cg = (vrect[1]+vrect[3])/2.0
            mean = 0

        return (rg,cg,mean)


def shift(target,r0,c0,w,adapt = 'none',N=10):
    """iterate the integralshift
    adapt parameter implement several converging strategies (still experimental)
    returns both last position and complete path up to it
    """
    path = np.zeros((N,2))
    r1 = r0-w/2.0
    c1 = c0-w/2.0
    r2 = r0+w/2.0
    c2 = c0+w/2.0
    path = [(r0,c0)]
    w0 = w
    rg = r0
    cg = c0
    for iter in range(0,N-1):
        rect = (r1,c1,r2,c2)
        rg,cg,mean = target.find_g(rect)
        mean_c= target.get_value(rg,cg)
        path.append([rg,cg])
        d2 = (r1+w/2.0-rg)**2+(c1+w/2.0-cg)**2
        if d2<.1:
            path.append([rg,cg])
            break
        if adapt is 'none':
            pass
        if adapt is 'iter_dec':
            w = w*.8
        if adapt is 'step_dec':
            w = .5*np.sqrt(d2)
        if adapt is 'intensity':
            w = w0*(1-mean_c)
        if adapt is 'custom':
            weight = [1.0]*5 + [.75]*5 + [.5]*5 + [.25]*(N-15)
            w = w0*weight[iter]
        r1 = rg-w/2.0
        c1 = cg-w/2.0
        r2 = rg+w/2.0
        c2 = cg+w/2.0

    return (rg,cg,np.asarray(path))

def test():
    """test integralshift on a grid
    """
    im = test_image(2)

    target = IntegratedImage(im)
    m,n = im.shape
    w = 20
    step = 5

    fig = plt.figure()
    ax = plt.axes([0,0,1,1])

    plt.imshow(im, interpolation='nearest')
    plt.colorbar()

    for r in range(0,m,step):
        for c in range(0,n,step):

            rg,cg,path = shift(target,r,c,w,adapt='none',N=40)

            start = mpatches.Circle((c,r), 0.5,fc=[1,1,1],ec='none',alpha=.25)
            stop = mpatches.Circle((cg,rg), 0.5,ec=[1,1,1],fc='none')

            arrow = mpatches.Arrow(c,r, cg-c, rg-r , width=0.5, color = 'y')
            line = mlines.Line2D(path[:,1], path[:,0], lw=.3, color = 'y')

            plt.gca().add_patch(start)
            plt.gca().add_patch(stop)
#            plt.gca().add_patch(arrow)
            ax.add_line(line)

if __name__ == "__main__":
    test()
    plt.show()



