Requirements
Linux host, gcc, make. Tested with gcc-4.8.0 and gcc-7.3.0
python2.7 - see requirements txt for python package requirements


# Components
 * depnetevo c++ code for running graph based analysis and expirements
 * python scripts for running the final calculations, tables and graphs


# Build depnetevo
* Download and compile SNAP 3.0 from http://snap.stanford.edu/snap/releases.html, extract and run `make`
* Update `SNAP_PATH` variable in depnetevo `Makefile` to point to folder where compiled SNAP is
* Compile depnetevo with make

# Steps
 * Convert data to graph format using  python
