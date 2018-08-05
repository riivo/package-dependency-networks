#!/bin/bash
export OMP_NUM_THREADS=4

# Generate graph file
mkdir -p ./working/
#python network_model.py Rust
#python network_model.py Ruby
#python network_model.py JS

# Run experiments, track evolution, size, vulnerability
mkdir -p ./working/experiments
cd working/experiments
../../depnetevo/depnetevo ../fixed_adopted_Rust_meta.csv Rust 1
../../depnetevo/depnetevo ../fixed_adopted_Rust_meta.csv Rust 0
../../depnetevo/depnetevo ../fixed_adopted_Ruby_meta.csv Ruby 1
../../depnetevo/depnetevo ../fixed_adopted_Ruby_meta.csv Ruby 0
../../depnetevo/depnetevo ../fixed_adopted_JS_meta.csv JS 1
../../depnetevo/depnetevo ../fixed_adopted_JS_meta.csv JS 0
cd ..
cd ..

# Aggregate experiments file into single files for ease of use
mkdir -p ./working/results/
python data_analysis_preprocessing.py


# Basic stats 
mkdir -p ./working/tables/
#python data_analysis_for_paper_stats.py Rust > ../working/tables/stats_rust.txt
#python data_analysis_for_paper_stats.py JS > ../working/tables/stats_js.txt
#python data_analysis_for_paper_stats.py RubyMerged > ../working/tables/stats_ruby.txt