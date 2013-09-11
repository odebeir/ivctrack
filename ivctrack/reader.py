# -*- coding: utf-8 -*-
'''Helper functions for image sequence crawling
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


from zipfile import ZipFile
import os.path as path
import re
import ImageFile
import numpy as np

from helpers import timeit,lru_cache

class Reader(object):
    """Provide a uniform interface for a generic sequence browser
    """
    def __init__(self,source):
        """a valid source should provide :
        * read_image(im_list[i]) that returns a numpy array
        * im_list a list of valid images (e.g. filenames,...)
        """
        self.source = source
        self.im_list = source.im_list
        self.head = 0

    def range(self):
        return range(len(self.im_list))

    def N(self):
        return len(self.im_list)

    def __str__(self):
        s = super(Reader, self).__str__()
        s = s + str(self.source)+' head:' + str(self.head)
        return s

    def rewind(self):
        """move the head to the first frame
        """
        self.head = 0
        return self.source.read_image(self.im_list[self.head][1])

    def ff(self):
        """move the head to the last frame
        """
        self.head = len(self.im_list)-1
        return self.source.read_image(self.im_list[self.head][1])

    def next(self):
        """move the head to the next frame, or raise a ValueError if the head is already on the last frame
        """
        self.head += 1
        if self.head > len(self.im_list):
            raise IndexError
        else:
            return self.source.read_image(self.im_list[self.head][1])

    def prev(self):
        """move the head to the previous frame, or raise a ValueError if the head is already on the first frame
        """
        self.head -= 1
        if self.head < 0 :
            raise IndexError
        else:
            return self.source.read_image(self.im_list[self.head][1])

    def moveto(self,frame):
        """Move head position to Frame (zero indexed)
        raise IndexError if out of bounds
        """
        self.head = frame
        if (self.head < 0) or (self.head > len(self.im_list)):
            raise IndexError
        else:
            return self.source.read_image(self.im_list[self.head][1])

    def getframe(self):
        """Returns the frame under the head
        """
        return self.source.read_image(self.im_list[self.head][1])

class ZipSource(object):
    """Object that is responsible for opening an experiment ZIP file containing all the images sequence
    it delivers a generator that serves all the sequence content
    """
    def __init__(self,filename,prefix = None):
        """create an object using the zipfile ´´filename´´
        """
        self.description = filename
        self.zipfilename = filename
        self.zf = ZipFile(self.zipfilename, 'r')
        self.build_image_list(prefix)

    def build_image_list(self,prefix = None):
        """returns a list of tuple of valid image filename contained in the zip file
        [(#frame,image_filename,extension)]
        """
        name_list = self.zf.namelist()

        if prefix is None:
    #        pattern = re.compile(r'(exp)([0-9]{4})', flags=re.IGNORECASE) #searching for images such as 'exp0001'
            pattern = re.compile(r'([^0-9]*)([0-9]*)', flags=re.IGNORECASE) #searching for images such as 'not_a_number01'
        else:
            pattern = re.compile('(%s)([0-9]*)'%prefix, flags=re.IGNORECASE) #searching for images such as 'not_a_number01'
            print pattern
        im_list = []
        t = 0 #zero indexed frame number
        for n in sorted(name_list):
            [name,ext] = path.splitext(n)
            m = pattern.match(name)
            if m:
                im_list.append((int(m.group(2)),n,ext[1:],t,m.group(1)))
                t += 1

        #analyse the serie
        if len(im_list):
            self.first = im_list[0][0]
            self.last = im_list[-1][0]
            #search for missing numbers
            self.missing = set(range(self.first,self.last+1)) - set([n for n,m,ext,t,prefix in im_list ])
        else:
            self.first = 0
            self.last = 0
            self.missing = set([])

        self.im_list = im_list

    def __str__(self):
        s = super(ZipSource, self).__str__()
        s = s + self.zipfilename+' first:%d'%self.first+' last:%d'%self.last+' #:%d'%len(self.im_list)
        return s

    def check_images(self):
        """crawls into the complete zip file and extract images infos
        """
        for n,f,ext in self.im_list:
            info=self.zf.getinfo(f)
            print info.date_time, info.compress_size, info.file_size
            ima = self.read_image(f)
            print ima.shape

    def parse_imagedata(self,data):
        """parse compressed image data
        returns a numpy array
        """
        p = ImageFile.Parser()
        p.feed(data)
        im = p.close()

        if im.mode == 'I;16B':
            r = np.asarray(im.im,dtype=np.uint16).reshape(im.size[-1::-1])
        else:
            r = np.asarray(im)

        # import matplotlib.pyplot as plt
        # plt.imshow(r)
        # plt.colorbar()
        # plt.show()

        return r

    @lru_cache(100)
    def read_image(self,image_name):
        """read compressed data and returns a numpy array
        """
        fid = self.zf.open(image_name)
        image_data = fid.read()
        im = self.parse_imagedata(image_data)
        return im

    def read_imagedata(self,image_name):
        """returns compressed image data
        """
        fid = self.zf.open(image_name)
        return fid.read()

    def generator(self,read_dir='fwd',first_frame = 0,last_frame = -1):
        """generate a list of numpy arrays from the zipfile
        read_dir = 'fwd' or 'rev'
        first_frame > last_frame (e.g. 5:10, 6:-5, -10:-6)
        """
        if read_dir not in ['fwd','rev']:
            raise ValueError("dir must be in ['fwd','rev']")
        if read_dir=='rev':
            for n,f,ext,t,prefix in self.im_list[last_frame:first_frame:-1]:
                yield (t,self.read_image(f))
        if read_dir=='fwd':
            for n,f,ext,t,prefix in self.im_list[first_frame:last_frame:1]:
                yield (t,self.read_image(f))

    def generator2(self):
        """generate a list of numpy arrays from the zipfile
        read first all the images in the compressed form into memory
        """
        #first read all the compressed images into memory
        raw_data = []
        for n,f,ext,t in self.im_list:
            raw_data.append(self.read_imagedata(f))

        for data in raw_data:
            yield (t,self.parse_imagedata(data))

class DumbSource(object):
    """Dumb sequence, generate a sequence of 10000 empty images (size (1,1))
    """
    def __init__(self,n=10000):
        """create an object using the zipfile ´´filename´´
        """
        self.n = n
        self.build_image_list()
        self.description = 'Dump sequence (%d)'%n

    def build_image_list(self):
        """returns a list of tuple of valid image filename contained in the zip file
        [(#frame,image_filename,extension)]
        """
        self.im_list = ['dumb%04d'%i for i in range(self.n)]
        self.first = 0
        self.last = self.n

    def __str__(self):
        s = super(DumbSource, self).__str__()
        s = s + self.zipfilename+' first:%d'%self.first+' last:%d'%self.last+' #:%d'%len(self.im_list)
        return s


    def read_image(self,image_name):
        """read compressed data and returns a numpy array
        """

        return np.zeros((1,1))

@timeit
def main():
    """open data sample
    """
    # JPG zip
    datazip_filename = '../test/data/seq0_extract.zip'
    prefix = 'exp'

    # TIF zip
    datazip_filename = '../test/data/Wetzel2013/NPC_track.zip'
    prefix = '20130607_Exp672_P001_C001_T'

#    datazip_filename = '../test/data/seq0.zip'

    source = ZipSource(datazip_filename,prefix)

#    source.check_images()
    g = source.generator()
    for frame,im in g:
       print frame,im,im.dtype,im.shape

    # #test the data access using a Reader
    # reader = Reader(source)
    # print reader.rewind()
    # while True:
    #     try:
    #         ima = reader.next()
    #         print ima
    #     except IndexError:
    #         break
    #
    # print reader.ff()
    # while True:
    #     try:
    #         print reader.prev().shape
    #     except IndexError:
    #         break
    #
    # reader.moveto(10)
    # print reader.head
    # print reader.getframe()

if __name__=='__main__':

    main()