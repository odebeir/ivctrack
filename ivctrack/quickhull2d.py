# Copyright (c) 2012 the authors listed at the following URL, and/or
# the authors of referenced articles or incorporated external code:
# http://en.literateprograms.org/Quickhull_(Python,_arrays)?action=history&offset=20091103134026
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Retrieved from: http://en.literateprograms.org/Quickhull_(Python,_arrays)?oldid=16555

from numpy import *

link = lambda a,b: concatenate((a,b[1:]))
edge = lambda a,b: concatenate(([a],[b]))
def qhull(sample):
    def dome(sample,base): 
        h, t = base
        dists = dot(sample-h, dot(((0,-1),(1,0)),(t-h)))
        outer = repeat(sample, dists>0, 0)

        if len(outer):
            pivot = sample[argmax(dists)]
            return link(dome(outer, edge(h, pivot)),
                        dome(outer, edge(pivot, t)))
        else:
            return base
    if len(sample) > 2:
        axis = sample[:,0]
        base = take(sample, [argmin(axis), argmax(axis)], 0)
        return link(dome(sample, base),
                    dome(sample, base[::-1]))
    else:
        return sample

if __name__ == "__main__":
    #sample = 10*array([(x,y) for x in arange(10) for y in arange(10)])
    sample = 100*random.random((32,2))
    hull = qhull(sample)
	
    print "%!"
    print "100 500 translate 2 2 scale 0 0 moveto"
    print "/tick {moveto 0 2 rlineto 0 -4 rlineto 0 2 rlineto"
    print "              2 0 rlineto -4 0 rlineto 2 0 rlineto} def"
    for (x,y) in sample:
        print x, y, "tick"
    print "stroke"
    print hull[0,0], hull[0,1], "moveto"
    for (x,y) in hull[1:]:
        print x, y, "lineto"
    print "closepath stroke showpage"
