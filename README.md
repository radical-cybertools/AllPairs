AllPairs
========

RADICAL Pilot Script
--------------------
#Installation

First you need to install Radical-Pilot on your system in a fresh virtualenv. Instructions can be found here:
http://radicalpilot.readthedocs.org/en/latest/installation.html#id1

Before running this script you need to install NumPy on your target system. On Stampede this can be done by:
```
module load intel/13.0.2.146
module load python
wget cython.org/release/Cython-0.21.tar.gz
tar xvfz Cython-0.21.tar.gz
cd Cython-0.21
python setup.py install --user                 
cd ..

git clone git://github.com/numpy/numpy.git numpy
cd numpy
python setup.py install --user                 
cd ..
```

Next, in rp_hausdorff.py make the following changes:
* Line 31 - add your username on target system (if your username on target system is the same as on your local system then comment out
lines 30-32)

* Line 39 - provide name of the target system. Default target system is Stampede.

* Line 42 - provide project name on target system (if you run this script locally comment out this line)

As a final step we must provide MongoDB url:
```
export RADICAL_PILOT_DBURL='mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'
```

Finally we can run the script:
```
python rp_hausdorff.py 2> debug.log
```

 
