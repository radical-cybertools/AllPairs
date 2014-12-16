import os
import sys
import saga
import radical.pilot as rp
from datetime import datetime
from datetime import timedelta

def pilot_state_cb (pilot, state) :
    print "[Callback]: ComputePilot '%s' state: %s." % (pilot.uid, state)
    if  state == rp.FAILED :
        sys.exit (1)

def unit_state_cb (unit, state) :
    print "[Callback]: ComputeUnit  '%s' state: %s." % (unit.uid, state)

def all_pairs (n) :
    ret = list ()
    for i in range (1, n+1) :
        for j in range (i+1, n+1) :
            ret.append ([i, j])
    return ret

#----------------------------------------------------------------------------
if __name__ == "__main__":
    print datetime.now()
    NUMBER_OF_TRAJECTORIES = 50
    MY_STAGING_AREA = 'staging:///'
    SHARED_HAUSDORFF = 'hausdorff.py'

    try:
        session   = rp.Session ()
        c         = rp.Context ('ssh')
        c.user_id = 'tg824689'
        session.add_context (c)

        print "initialize pilot manager ..."
        pmgr = rp.PilotManager (session=session)
        pmgr.register_callback (pilot_state_cb)

        pdesc = rp.ComputePilotDescription ()
        pdesc.resource = "xsede.stampede"
        pdesc.runtime  = 540 # minutes
        pdesc.cores    = 64
        pdesc.project  = "TG-MCB090174"
        pdesc.cleanup  = False

        # submit the pilot.
        print "submit pilot ..."
        pilot = pmgr.submit_pilots (pdesc)

        print "initialize unit manager ..."
        umgr = rp.UnitManager  (session=session, scheduler=rp.SCHED_BACKFILLING)
        umgr.register_callback (unit_state_cb)

        print "add pilot to unit manager ..."
        umgr.add_pilots(pilot)

        print "stage shared data ..."
        fshared_list   = list()
        
        # list of files to stage: the script, and the 5 trajectories
        fnames = list()
        fnames.append ('hausdorff.py')

        for idx in range (1, NUMBER_OF_TRAJECTORIES+1) :
            fnames.append ('traj%d.npz.npy' %      idx)
        
        fname_stage = []
        # stage all files to the staging area
        for fname in fnames :
            src_url = 'file://%s/%s' % (os.getcwd(), fname)

            sd_pilot = {'source': src_url,
                        'target': os.path.join(MY_STAGING_AREA, fname),
                        'action': rp.TRANSFER,
            }

            fname_stage.append (sd_pilot)
           
        # Synchronously stage the data to the pilot
        pilot.stage_in(fname_stage)

        print "describe compute units ..."

        print "all pairs: "
        print all_pairs ( NUMBER_OF_TRAJECTORIES )
        # we create one CU for each unique pair of trajectories
        cudesc_list = []
        for i, j in all_pairs (NUMBER_OF_TRAJECTORIES) :

            print "define unit for pair %d / %d" % (i,j)
            # shared data directives for the script and the two trajectories
            print "Simlinked input files for a pair: "
            print os.path.join(MY_STAGING_AREA, SHARED_HAUSDORFF)
            print os.path.join(MY_STAGING_AREA, ( 'traj%d.npz.npy' % i  ))
            print os.path.join(MY_STAGING_AREA, ( 'traj%d.npz.npy' % j  ))

            fshared_0 = {'source': os.path.join(MY_STAGING_AREA, SHARED_HAUSDORFF),
                         'target': SHARED_HAUSDORFF,
                         'action': rp.LINK}

            fshared_1 = {'source': os.path.join(MY_STAGING_AREA, ( 'traj%d.npz.npy' % i  )),
                         'target': 'traj%d.npz.npy' % i,
                         'action': rp.LINK}

            fshared_2 = {'source': os.path.join(MY_STAGING_AREA, ( 'traj%d.npz.npy' % j  )),
                         'target': 'traj%d.npz.npy' % j,
                         'action': rp.LINK}

            # define the compute unit, to compute over the trajectory pair
            cudesc = rp.ComputeUnitDescription()
            cudesc.executable    = "python"
            cudesc.pre_exec      = ["module load python/2.7.3-epd-7.3.2"]
            cudesc.input_staging = [fshared_0, fshared_1, fshared_2]
            cudesc.arguments     = ['hausdorff.py', '-v', i, j]
            cudesc.cores         = 1

            cudesc_list.append (cudesc)

        # submit, run and wait and...
        print "submit units to unit manager ..."
        units = umgr.submit_units (cudesc_list)

        print "wait for units ..."
        starting_time = datetime.now()
        umgr.wait_units()
        ending_time = datetime.now()

        units_total_time = timedelta(0)

        fp=open('./results/output_%d_traj_stampede_32cores.log'%NUMBER_OF_TRAJECTORIES,'w')
        comp_starting_time = list()
        comp_ending_time = list()
        #... voila!
        for unit in units :
            print "* Unit %s @ %s \n"      \
                  "\t   state    : %s\n"   \
                  "\t   exit code: %s\n"   \
                  "\t   started  : %s\n"   \
                  "\t   finished : %s\n"   \
                  "\t   output   : %s\n"   \
                  "\t   error    : %s\n\n" \
                % (unit.uid,       unit.execution_locations, unit.state, 
                   unit.exit_code, unit.start_time,          unit.stop_time,
                   unit.stdout,    unit.stderr)
            comp_starting_time.append(unit.start_time)
            comp_ending_time.append(unit.stop_time)
            fp.write("* Unit %s @ %s \n"   \
                  "\t   state    : %s\n"   \
                  "\t   exit code: %s\n"   \
                  "\t   started  : %s\n"   \
                  "\t   finished : %s\n"   \
                  "\t   output   : %s\n"   \
                  "\t   error    : %s\n\n" \
                % (unit.uid,       unit.execution_locations, unit.state, 
                   unit.exit_code, unit.start_time,          unit.stop_time,
                   unit.stdout,    unit.stderr))
            units_total_time = units_total_time + unit.stop_time - unit.start_time
        comp_ending_time.sort()
        comp_starting_time.sort()
        print "Total Time (in secs) is ",(ending_time-starting_time).total_seconds()
        print "Total Execution Time (in secs) is ",(comp_ending_time[-1]-comp_starting_time[0]).total_seconds()
        print "Summation of Units Execution Time (in secs) is ", units_total_time.total_seconds()
        fp.write("Total Time (in secs) is %f\n"%(ending_time-starting_time).total_seconds())
        fp.write("Total Execution Time (in secs) is %f\n"%(comp_ending_time[-1]-comp_starting_time[0]).total_seconds())
        fp.write("Summation of Units Execution Time (in secs) is %f\n"%units_total_time.total_seconds())
        fp.write("First CU started @ %s\n"%comp_starting_time[0])
        fp.write("Last CU ended @ %s\n"%comp_ending_time[-1])
        fp.close()
    except Exception as e:
        import traceback
        traceback.print_exc ()
        print "An error occurred: %s" % ((str(e)))
        sys.exit (-1)

    except KeyboardInterrupt :
        print "Execution was interrupted"
        sys.exit (-1)

    finally :
        print "Closing session, exiting now ..."
        session.close()
        print datetime.now()

