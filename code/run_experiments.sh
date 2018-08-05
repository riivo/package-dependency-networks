#!/bin/bash
export OMP_NUM_THREADS=2

#python network_model.py Rust
#python network_model.py Ruby
#python network_model.py JS

cd working/experiments
../../depnetevo/depnetevo ../fixed_adopted_Rust_meta.csv Rust 1
../../depnetevo/depnetevo ../fixed_adopted_Rust_meta.csv Rust 0

cd ..
cd ..
