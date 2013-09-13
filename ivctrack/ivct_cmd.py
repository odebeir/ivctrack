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
def test_source(source,prefix=None):
    from reader import ZipSource
    source = ZipSource(source,prefix)
    print source

def test_marks(filename):
    from cellmodel import import_marks
    m = import_marks(filename)
    print m

def track(source,dir,marks,hdf5,params,prefix):
    import json
    s = json.loads(open(params).read())
    print s
    from cellmodel import test_experiment
    test_experiment(datazip_filename=source,marks_filename=marks,hdf5_filename=hdf5,dir=dir,params=s,prefix=prefix)

def play(source,hdf5):
    from player import test_player
    test_player(datazip_filename=source,hdf5filename=hdf5)

def gui(source):
    from chaco_gui import test_gui
    test_gui(source)

def plot(hdf5_filename):
    from measurement import test_plot
    test_plot(hdf5_filename)

def set_marks(datazip_filename,frame,mark_filename):
    from reader import Reader,ZipSource
    import matplotlib.pyplot as plt

    reader = Reader(ZipSource(datazip_filename))
    print reader
    reader.moveto(frame)
    bg = reader.getframe()
    fig = plt.figure()
    plt.imshow(bg)
    xy = plt.ginput(n=0)
    plt.close(fig)
    t = reader.head
    print xy,t
    fid = open(mark_filename,'w+t')
    for x,y in xy:
        fid.write('%f,%f,%d\n'%(x,y,t))
    del fid
    print 'marks saved in ',mark_filename

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='IVCT_CMD',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #positional arguments
    subparsers = parser.add_subparsers( title='subcommands',
                                        description='valid subcommands',
                                        help='additional help (e.g. type "ivct_cmd track --help").')

    parser_test = subparsers.add_parser('test', help='test a zipped sequence file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_test.add_argument("--seq", type=str,help="image sequence (.zip)",required=True)
    parser_test.set_defaults(mode='test')

    parser_mark = subparsers.add_parser('mark', help='marks the n-th frame of a zipped sequence file, save marks in a .csv file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_mark.add_argument("--seq", type=str,help="image sequence (.zip)",required=True)
    parser_mark.add_argument("--marks", type=str,help="marks file (.csv)",default='marks.csv')
    parser_mark.add_argument("--frame", type=int,help="frame where to place marks (-1 is last frame etc)",default=1)
    parser_mark.set_defaults(mode='mark')

    parser_track = subparsers.add_parser('track', help='track a zipped sequence file using marks',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_track.add_argument("--seq", type=str,help="image sequence (.zip)",required=True)
    parser_track.add_argument("--marks", type=str,help="initial tracking positions (.csv)",default='defmarks.csv')
    parser_track.add_argument("--dir", choices=['fwd','rev','both'],help="tracking direction",default='fwd')
    parser_track.add_argument("--hdf5", type=str,help="HDF5 destination filepath",default='tracks.hdf5')
    parser_track.add_argument("--params", type=str,help="parameters file (.json)",default='parameters.json')
    parser_track.add_argument("--prefix", type=str,help="image prefix",default=None)
    parser_track.set_defaults(mode='track')

    parser_play = subparsers.add_parser('play', help='play a tracked sequence',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_play.add_argument("--seq", type=str,help="image sequence (.zip)",required=True)
    parser_play.add_argument("--hdf5", type=str,help="HDF5 filepath",default='tracks.hdf5')
    parser_play.set_defaults(mode='play')

    parser_gui = subparsers.add_parser('gui', help='display a graphical interactive view for model parameters fitting',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_gui.add_argument("--seq", type=str,help="image sequence (.zip)",required=True)
    parser_gui.set_defaults(mode='gui')

    parser_plot = subparsers.add_parser('plot', help='plot a tracked sequence',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_plot.add_argument("--hdf5", type=str,help="HDF5 filepath",default='tracks.hdf5')
    parser_plot.set_defaults(mode='plot')

    parser_export = subparsers.add_parser('export', help='export a tracked sequence',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_export.add_argument("--hdf5", type=str,help="HDF5 filepath",default='tracks.hdf5')
    parser_export.set_defaults(mode='export')


    args = parser.parse_args()

    print 'MODE:',args.mode

    if args.mode == 'test':
        print args.seq
        test_source(args.seq)

    if args.mode == 'mark':
        print 'interactive marks setting'
        print
        set_marks(datazip_filename=args.seq,mark_filename=args.marks,frame=args.frame)

    if args.mode == 'track':
        if args.seq is not None:
            print 'source=',args.seq
            test_source(args.seq,args.prefix)
        else:
            print '--seq needed'
            parser.print_usage()
            exit(1)
        print 'dir=',args.dir
        track(source=args.seq,dir=args.dir,marks=args.marks,hdf5=args.hdf5,params=args.params,prefix=args.prefix)

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

    if args.mode == 'gui':
        if args.seq is not None:
            print 'source=',args.seq
            test_source(args.seq)
        else:
            print '--seq needed'
            parser.print_usage()
            exit(1)
        gui(args.seq)

    if args.mode == 'plot':
        plot(args.hdf5)

    if args.mode == 'export':
        print 'not implemented yet'
