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
from scipy.stats import linregress

#-------SPEED---------------------------------------------------------------------------------------
def inst_speed(xy):
    s = npy.sqrt(npy.sum(npy.diff(xy,axis=0)**2,axis=1))
    return s

def path_length(xy):
    return npy.sum(inst_speed(xy))

def avg_speed(xy):
    """
    >>> xy = npy.asarray([[0,0],[0,1],[1,1],[1,0]])
    >>> print avg_speed(xy)
    0.75
    """
    return path_length(xy)/xy.shape[0]

def mrdo_speed(xy):
    """
    >>> xy = npy.asarray([[0,0],[0,1],[1,1],[1,0]])
    >>> print mrdo_speed(xy)
    0.353553390593
    """
    xy0 = xy[0,:]
    d = npy.sqrt(npy.sum((xy-xy0)**2,axis=1))
    d_max = npy.max(d)
    return d_max/xy.shape[0]

def area_of_triangle(p1, p2, p3):
    '''calculate area of any triangle given co-ordinates of the corners

    >>> p1 = npy.asarray([0,0])
    >>> p2 = npy.asarray([1,0])
    >>> p3 = npy.asarray([1,1])
    >>> print area_of_triangle(p1,p2,p3)
    0.5
    '''

    return npy.linalg.norm(npy.cross((p2 - p1), (p3 - p1)))/2.

def hull_speed(xy):
    """
    >>> xy = npy.asarray([[0,0],[0,1],[1,1],[1,0]])
    >>> print hull_speed(xy)
    (0.25, 0.35355339059327379)
    """
    hull_xy = qhull(xy)
    #max dist inside hull
    d = pdist(hull_xy, 'euclidean')
    dmax_idx = npy.argmax(d)
    #hull_surf
    p3 = npy.mean(hull_xy,axis=0)
    n_hull = hull_xy.shape[0]
    hull_surf = 0.0
    for k in range(n_hull):
        p1 = hull_xy[k,:]
        p2 = hull_xy[(k+1)%n_hull,:]
        a = area_of_triangle(p1,p2,p3)
        hull_surf += a

    return (hull_surf/xy.shape[0],d[dmax_idx]/xy.shape[0])

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

#-------DIRECTION---------------------------------------------------------------------------------------
def scaling_exponent(xy):
    """computes the Hurst coefficient which qualify how the trajectory is persistent in time
    it is related to the fractal dimension of the trajectory
    """
    #compute all distances
    d = squareform(pdist(xy, 'sqeuclidean'))

    #max number of successive positions
    N = 15
    data = npy.zeros((N,2))

    for k in range(N):
        kd = npy.diag(d,k+1)
        data[k,:] = (k+1,npy.mean(kd))


    #linear fit in log-log
    x = npy.log(data[:,0])
    y = npy.log(data[:,1])
    slope, intercept, r_value, p_value, std_err = linregress(x,y)

#    print slope, r_value, std_err
#    fig = plt.figure()
#    ax = fig.add_subplot(111, aspect='equal')
##    plt.plot(data[:,0],data[:,1])
#    plt.plot(x,y)
#    plt.show()
    return (slope,r_value**2)

def hurst_curv_exponent(xy):
    """computes the Hurst coefficient which qualify how the trajectory is persistent in time
    it is related to the fractal dimension of the trajectory, here the denominator is the curvilinear distance
    """
    #compute all distances
    d = squareform(pdist(xy, 'euclidean'))

    #max number of successive positions
    N = 10
    data = npy.zeros((N,2))

    for k in range(N):
        kd = npy.diag(d,k+1)
        c_length = k+1
        data[k,:] = (c_length,npy.mean(kd))

    #linear fit in log-log
    x = npy.log(data[:,0])
    y = npy.log(data[:,1])
    A = npy.vstack([x, npy.ones(len(x))]).T
    m, c = npy.linalg.lstsq(A, y)[0]

    #    fig = plt.figure()
    #    ax = fig.add_subplot(111, aspect='equal')
    #    plt.loglog(data[:,0],data[:,1])
    #    plt.legend()
    #    plt.show()
    return m

def relative_direction_distribution(xy):
    """computes instantaneous directions and make an histogram centered on previous direction
    """
    dxy = xy[1:,:]-xy[0:-1,:]
    theta = npy.arctan2(dxy[:,0],dxy[:,1])
    rho = npy.sqrt(npy.sum(dxy**2,axis=1))
    dtheta = theta[1:]-theta[0:-1]
    dtheta = npy.hstack(([0],dtheta))
    clip_dtheta = dtheta.copy()
    clip_dtheta[dtheta>npy.pi] = dtheta[dtheta>npy.pi] - npy.pi
    clip_dtheta[dtheta<-npy.pi] = dtheta[dtheta<-npy.pi] + npy.pi

    N = 8
    width = 2*npy.pi/N
    offset_th = .5*width
    bins = npy.linspace(-npy.pi-offset_th,npy.pi+offset_th,N+2,endpoint=True)
    print 'bins',bins
    h_theta,bin_theta = npy.histogram(clip_dtheta,bins=bins,weights=rho)
    print 'h',h_theta

    h_theta[0]+=h_theta[-1]

    dx = rho*npy.cos(dtheta)
    dy = rho*npy.sin(dtheta)


    #resulting direction
#    tot_theta = npy.arctan2(tot_dxy[0],tot_dxy[1])
#    tot_rho = npy.sqrt(npy.sum(tot_dxy**2))

    import matplotlib.pyplot as plt
    fig=plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
#    ax.bar(bin_theta[0:-1], npy.ones_like(bin_theta[0:-1]), width=width, bottom=0.0,alpha=.5)
    ax.bar(bin_theta[0:-2], h_theta[:-1], width=width, bottom=0.0)
#    plt.plot(h[0])
#    plt.plot(dx,dy)
    plt.polar(clip_dtheta,rho, 'ro')
#    plt.polar(dtheta,rho+.1, 'bo')
#    plt.hist(dtheta)
#    plt.figure()
#    plt.hist(clip_dtheta)
#    plt.polar(tot_theta,tot_rho, 'bo')

    plt.show()
    return 0
#----------------------------------------------------------------------------------------------

def speed_feature_extraction(hdf5_filename):

    features,data = get_hdf5_data(hdf5_filename,fields=['center'])
    measures = []
    feat_name = ['path_length','avg_speed','mrdo','hull_surf','hull_dist']
    for d in data:
        xy = d['center']
        pl = path_length(xy)
        avg = avg_speed(xy)
        mrdo = mrdo_speed(xy)
        hull_surf, hull_d = hull_speed(xy)
        measures.append((pl,avg,mrdo,hull_surf,hull_d))
    measures = npy.asarray(measures)

    return (feat_name,measures)

def direction_feature_extraction(hdf5_filename):

    features,data = get_hdf5_data(hdf5_filename,fields=['center'])
    measures = []
    feat_name = ['scaling_exponent','scaling_exponent_r2']
    for d in data:
        xy = d['center']
        se,se_err = scaling_exponent(xy)
#        hurst_c = hurst_curv_exponent(xy)
        relative_direction_distribution(xy)
        measures.append((se,se_err))

    measures = npy.asarray(measures)

    return (feat_name,measures)


if __name__=='__main__':

    import doctest

    print doctest.testmod()

    hdf5_filename = '../test/data/test_rev.hdf5'

    c_feat,c_data = get_hdf5_data(hdf5_filename,fields=['center'])

    s_feat,s_data = speed_feature_extraction(hdf5_filename)
    print s_feat
    print s_data

    d_feat,d_data = direction_feature_extraction(hdf5_filename)
    print d_feat
    print d_data

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    rank = npy.argsort(d_data[:,0])
    for i,r in enumerate(rank):
        xy = c_data[r]['center']
        p_length = s_data[r,0]
        x0 = xy[0,0]
        y0 = xy[0,1]
        offset_x = s_data[r,4]*1000
#        offset_x = p_length*10
#        offset_x = s_data[r,3]*100
        offset_y = d_data[r,0]*1000
        plt.plot(xy[:,0]-x0+offset_x,xy[:,1]-y0+offset_y)
#        plt.text(xy[0,0]-x0+offset_x,xy[0,1]-y0+offset_y,'%.3f(%.3f)'%(d_data[r,0],d_data[r,1]))

#    plt.show()

