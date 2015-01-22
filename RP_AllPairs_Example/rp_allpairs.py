import os
import sys
import saga
import radical.pilot as rp
from datetime import datetime
from datetime import timedelta

def pilot_state_cb (pilot, state) :
    '''
    Pilot's Callback Function. Defines how the messages for the pilot's
    state will be displayed
    '''
    print "[Callback]: Pilot '%s' state: %s." % (pilot.uid, state)
    if  state == rp.FAILED :
        sys.exit (1)

def unit_state_cb (unit, state) :
    '''
    Compute Unit's Callback Function. Defines how the messages for the Compute
    Unit's state will be displayed
    '''
    print "[Callback]: Compute Unit  '%s' state: %s." % (unit.uid, state)

def comparisons (n) :
    ret = list ()
    for i in range (1, n+1) :
        for j in range (i+1, n+1) :
            ret.append ([i, j])
    return ret

#---------------------------------------------------------------------------------
if __name__ == "__main__":

    '''
    The main function of the Radical Pilot All Pairs example script
    '''

    # The number of files that will be compared in the all-pairs fassion
    NUMBER_OF_FILES = 10
    #The URL for the staging area
    STAGING_AREA = 'staging:///'
    NUM_COMP = comparisons(NUMBER_OF_FILES)

    try:
        # Here the Radical Pilot Session is defined.
        session   = rp.Session()
        c         = rp.Context('ssh') # Connection type to the remote target machine
        c.user_id = '' #The user name for the remote target machine
        session.add_context(c)
        
        print "Initialize Pilot Manager..."
        pmgr = rp.PilotManager(session=session)
        pmgr.register_callback(pilot_state_cb)
        
        #Pilot's Description Section. Contains the alias for the remote machine,
        # the wall time of the pilot in minutes, the number of cores that will
        # be allocated by the pilot, the project name.
        PilotDescr = rp.ComputePilotDescription()
        PilotDescr.resource = "xsede.stampede"
        PilotDescr.runtime  = 40 #Always in minutes
        PilotDescr.cores    = 4
        PilotDescr.project  = ""
        PilotDescr.cleanup  = False

        #Submitting Pilot
        print 'Submitting Pilot...............'
        Pilot = pmgr.submit_pilots(PilotDescr)

        print "Unit Manager Initialization"
        umgr = rp.UnitManager(session=session,
            scheduler=rp.SCHED_BACKFILLING)
        umgr.register_callback(unit_state_cb)

        print "Add Pilot to Unit Manager"
        umgr.add_pilots(Pilot)

        #Describe Compute Units
        CUDesc_list = list()
        for i in range(1,NUMBER_OF_FILES+1):
            #Output File Staging. The file after it is created in the folder of each CU, is moved to the folder defined in
            #the start of the script
            OUTPUT_FILE           = {'source':'asciifile-{0}.dat'.format(i),
                                    'target':os.path.join(STAGING_AREA,"asciifile-{0}.dat".format(i)),
                                    'action':rp.MOVE}
            cudesc                = rp.ComputeUnitDescription()
            cudesc.executable     = '/bin/bash' # The executable that will be executed by the CU
            cudesc.output_staging = [OUTPUT_FILE]
            # The arguments of the executable
            cudesc.arguments      = ['-l', '-c', 'base64 /dev/urandom | head -c 1048576 > %s'%OUTPUT_FILE['source']]
            # The number of Cores the CU will use.
            cudesc.cores          = 1

            CUDesc_list.append(cudesc)

        print "Submitting Units to Unit Manager"
        Units = umgr.submit_units(CUDesc_list)

        print "Waiting for Units"
        umgr.wait_units()

        for unit in Units :
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

        #Describe Compute Units
        CUDesc_list = list()

        for i,j in comparisons(NUMBER_OF_FILES):
            INPUT_FILE1           = {'source': os.path.join(STAGING_AREA, "asciifile-{0}.dat".format(i)),
                                    'target' : "asciifile-{0}.dat".format(i),
                                    'action' : rp.LINK}
            INPUT_FILE2           = {'source': os.path.join(STAGING_AREA, "asciifile-{0}.dat".format(j)),
                                    'target' : "asciifile-{0}.dat".format(j),
                                    'action' : rp.LINK}
            OUTPUT_FILE           = "comparison-{0}-{1}.log".format(i, j)
            cudesc                = rp.ComputeUnitDescription()
            cudesc.executable     = '/bin/bash'
            cudesc.input_staging  = [INPUT_FILE1, INPUT_FILE2]
            cudesc.output_staging = [OUTPUT_FILE]
            cudesc.arguments      = ['-l', '-c', 'diff -U 0 %s %s | grep ^@ | wc -l > %s'%(INPUT_FILE1['target'],INPUT_FILE2['target'],OUTPUT_FILE)]
            cudesc.cores          = 1

            CUDesc_list.append(cudesc)

        print "Submitting Units to Unit Manager"
        Units = umgr.submit_units(CUDesc_list)

        print "Waiting for Units"
        umgr.wait_units()

        for unit in Units :
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
    except Exception as e:
        import traceback
        traceback.print_exc ()
        print "An error occurred: %s" % ((str(e)))
        sys.exit (-1)

    except KeyboardInterrupt :
        print "Execution was interrupted"
        sys.exit (-1)

    finally:
        print "Closing Pilot Session"
        session.close()

