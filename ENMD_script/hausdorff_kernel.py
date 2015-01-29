import sys, getopt
import numpy as np
np.set_printoptions(precision=3)

def main(argv):
    global _verbose
    _verbose = False
    try:
        usagestr = 'hausdorff_kernel.py -v <verbose>'
        opts, args = getopt.getopt(argv,"hv", ["help", "verbose"])
    except getopt.GetoptError:
        print usagestr
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "-help", "--help"):
            print usagestr
            sys.exit()
        elif opt in ("-v", "--verbose"):
            _verbose = True

    # if _verbose: print 'Trajectory numbers:', args[:2]
    return args[:3], _verbose

def vsqnorm(v, axis=None):
        '''
           Compute the conventional norm of an N-dimensional vector.
        '''
        return np.sum(v*v, axis=axis)

def RMSD_matrix(P, Q, axis=(1,2)):
    return np.array([vsqnorm(pt - Q, axis=axis) for pt in P])


if __name__ == "__main__":
    inputfiles, _verbose = main(sys.argv[1:])

    traj1 = np.load(inputfiles[0])
    traj2 = np.load(inputfiles[1])
    out   = open(inputfiles[2],'w')


    
    if len(traj1.shape) == 3:
        axis = (1,2)
        Ni = 1./traj1.shape[1]
    else:
        axis = 1
        Ni = 3./traj1.shape[1]

    d = RMSD_matrix(traj1, traj2, axis=axis)
    
    dH = ( max(d.min(axis=0).max(), d.min(axis=1).max())*Ni )**0.5

    out.write(str(dH))
    out.close()

    if _verbose: print dH
