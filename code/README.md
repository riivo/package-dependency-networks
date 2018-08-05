# Code for analyzing dependency network structure and evolution

# Requirements
* Linux host, gcc, make. Tested with gcc-4.8.0 and gcc-7.3.0
* python2.7 - see requirements txt for python package requirements
* Intermediate steps might require up to 10G of disk space. It requires at least 32GB of RAM and approximately 12 hours to run everything


# Components
 * depnetevo c++ code for running graph based analysis and expirements
 * python scripts for running the final calculations, tables and graphs


# Build depnetevo
* Download and compile SNAP 3.0 from http://snap.stanford.edu/snap/releases.html, extract and run `make`
* Update `SNAP_PATH` variable in depnetevo `Makefile` to point to folder where compiled SNAP is
* Compile depnetevo with make

# Steps to invoke
 * Clone the repo as is
 * Change working directory to this directory and run run_experiments.sh script that invokes experiments and runs the scripts that generates figures and stats used in the paper
 * The output figures are stored in working/figures and tables in working/tables