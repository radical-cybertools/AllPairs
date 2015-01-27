AllPairs
========

#RADICAL Pilot Script Usage
--------------------
##Installation

First you need to install Radical-Pilot on your system in a fresh virtualenv. Instructions can be found here:
http://radicalpilot.readthedocs.org/en/latest/installation.html#id1

Please before running the script to a remote machine set a passwordless ssh connection.
Instructions can be found here:

http://www.linuxproblem.org/art_9.html

##Simple Script

In rp_hausdorff.py make the following changes:
* Line 33 - add your username on target system (if your username on target system is the same as on your local system then comment out
lines 32-34)

* Line 41 - provide name of the target system. Default target system is Stampede (xsede.stampede).

* Line 44 - provide project name on target system (if you run this script locally comment out this line)

As a final step we must provide MongoDB url:
```
export RADICAL_PILOT_DBURL='mongodb://ec2-54-221-194-147.compute-1.amazonaws.com:24242/'
```

Finally we can run the script:
```
python rp_hausdorff.py
```
 
##Optimized Script

In rp_hausdorff_opt.py make the following changes:
* Line 31 - Set the path where the trajectory files exist in the target machine.

* Line 38 - add your username on target system (if your target system is your local system then comment out lines 37-39)

* Line 46 - provide name of the target system. Default target system is Stampede (xsede.stampede).

* Line 44 - provide project name on target system (if you run this script locally comment out this line)

As a final step we must provide MongoDB url:
```
export RADICAL_PILOT_DBURL='mongodb://ec2-54-221-194-147.compute-1.amazonaws.com:24242/'
```

Finally we can run the script:
```
python rp_hausdorff_opt.py
```