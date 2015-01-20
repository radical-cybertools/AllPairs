#!/usr/bin/env python

import sys, getopt,ast
import numpy as np
import argparse
import gc


def dH((P, Q)):
    def vsqnorm(v, axis=None):
        return np.sum(v*v, axis=axis)
    Ni = 3./P.shape[1]
    d = np.array([vsqnorm(pt - Q, axis=1) for pt in P])
    return ( max(d.min(axis=0).max(), d.min(axis=1).max())*Ni )**0.5


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("start", help="Enter number of starting trajectory")
    parser.add_argument("end", help="Enter number of ending trajectory")
    parser.add_argument("sel", help="Enter aa, ha, or ca for atom selection")
    parser.add_argument("size", help="Trajectories length. Valid Values: short,med,long. Default Value: short")
    parser.add_argument("pairs", help="A list with the pairs that will be checked")
    args = parser.parse_args()

    start, end = int(args.start), int(args.end)
    sel = args.sel
    pairs = ast.literal_eval(args.pairs)
    size = args.size
    if size == 'med':
        print "Medium"
        trj_list = [np.hstack( ( np.load('trj_%s_%03i.npz.npy' % (sel, i)),    \
                                 np.load('trj_%s_%03i.npz.npy' % (sel, i)) ) ) \
                                 for i in xrange(start,end+1)]
    elif size == 'long':
        print "Long"
        trj_list = [np.hstack( ( np.load('trj_%s_%03i.npz.npy' % (sel, i)),    \
                                 np.load('trj_%s_%03i.npz.npy' % (sel, i)),    \
                                 np.load('trj_%s_%03i.npz.npy' % (sel, i)),    \
                                 np.load('trj_%s_%03i.npz.npy' % (sel, i)) ) ) \
                                 for i in xrange(start,end+1)]
    else:
        print "Short"
        trj_list = [np.load('trj_%s_%03i.npz.npy' % (sel, i)) for i in xrange(start,end+1)]

    for pair in pairs:
        comp=dH((trj_list[pair[0]-start],trj_list[pair[1]-start]))
        print pair,':',comp