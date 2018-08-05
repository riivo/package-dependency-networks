#!/bin/bash
mkdir -p ../working/tables/
python data_analysis_for_paper_stats.py Rust > ../working/tables/stats_rust.txt
python data_analysis_for_paper_stats.py JS > ../working/tables/stats_js.txt
python data_analysis_for_paper_stats.py RubyMerged > ../working/tables/stats_ruby.txt

