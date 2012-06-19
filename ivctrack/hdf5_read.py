# -*- coding: utf-8 -*-
'''This file contains the HDF5 function needed to import results files and extract its datasets
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

#generic import
from datetime import datetime
import numpy as npy
import csv

#specific import
import h5py

def get_hdf5_info(filename):
    """returns basic information from the HDF5 structure
    """
    fid = h5py.File(filename, 'r')
    print fid
    for g in fid:
        print g



if __name__ == "__main__":

    get_hdf5_info('../test/temp/test.hdf5')


