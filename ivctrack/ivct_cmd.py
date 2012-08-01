# -*- coding: utf-8 -*-
'''main command line program that provides a simple interface to tracking utilities
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
def test_source(source):
    from reader import ZipSource
    source = ZipSource(source)
    print source

def test_marks(filename):
    from cellmodel import import_marks
    m = import_marks(filename)
    print m

def track(source,dir,marks,hdf5):
    from cellmodel import test_experiment
    test_experiment(datazip_filename=source,marks_filename=marks,hdf5_filename=hdf5,dir=dir)

def play(source,hdf5):
    from player import test_player
    test_player(datazip_filename=source,hdf5filename=hdf5)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='IVCT_CMD',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #positional arguments
    parser.add_argument("mode", type=str,help="type of action to be done : test/track")
    #optional arguments
    parser.add_argument("--seq", type=str,help="image sequence (.zip)")
    parser.add_argument("--marks", type=str,help="initial tracking positions (.csv)")
    parser.add_argument("--dir", choices=['fwd','rev','both'],help="tracking direction",default='fwd')
    parser.add_argument("--hdf5", type=str,help="HDF5 destination filepath",default='tracks.hdf5')
    parser.add_argument("--verbose", help="increase output verbosity",action="store_true")
    args = parser.parse_args()

    print 'MODE:',args.mode

    if args.verbose:
        print 'verbose mode'

    if args.mode == 'test':
        if args.seq is not None:
            print args.seq
            test_source(args.seq)
        else:
            print '--seq needed'
            parser.print_usage()
            exit(10)

    if args.mode == 'track':
        if args.seq is not None:
            print 'source=',args.seq
            test_source(args.seq)
        else:
            print '--seq needed'
            parser.print_usage()
            exit(1)

        if args.marks is not None:
            print 'marks=',args.marks
            test_marks(args.marks)
        else:
            print '--marks needed'
            parser.print_usage()
            exit(2)

        if args.hdf5 is not None:
            print 'hdf5=',args.hdf5
        else:
            print '--hdf5 needed'
            parser.print_usage()
            exit(3)

        print 'dir=',args.dir

    if args.mode == 'play':
        if args.seq is not None:
            print 'source=',args.seq
            test_source(args.seq)
        else:
            print '--seq needed'
            parser.print_usage()
            exit(1)

        if args.hdf5 is not None:
            print 'hdf5=',args.hdf5
        else:
            print '--hdf5 needed'
            parser.print_usage()
            exit(3)

        play(args.seq,args.hdf5)
