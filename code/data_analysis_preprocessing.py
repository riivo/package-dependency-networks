# -*- coding: utf-8 -*-
"""
Generates required files for data analysis

Created on Thu Aug 04 14:30:28 2016

@author: Riivo
"""
import pandas as pd
import glob 
import gc
import config

def collect_results(str1, ver=False):
    results = []
    df_ = None
    for fname in glob.glob(str1):
        names_ = ["project_github","project_name","size","max_depth","unique", "indegree", "outdegree", "uniq_degree", "pagerank", "unique_published"]
        if ver:
            names_ = ["project_github","project_name","project_ver", "size","max_depth","unique", "indegree", "outdegree","uniq_degree", "pagerank","unique_published"]
        df = pd.read_csv(fname, sep="\t",skiprows=0,header=None,na_values="", names=names_, index_col=None)
        tsindex=3
        if ver: tsindex+=1
        timestamp = fname.split("-")[tsindex].rstrip(".tsv").rstrip("rev").rstrip("-orig")
        #print timestamp
        df["date"] = pd.to_datetime(timestamp, unit="s")
        df["date"] = pd.DatetimeIndex(df.date).normalize()
        #results.append(df)
        if df_ is None:
            df_ = df
        else:
            df_ = pd.concat([df_,df])
    
    #df_ = pd.concat(results)
    return df_
    
if __name__ == "__main__":
    for lang in ["Rust", "JS", "Ruby"]:
        print lang
        regular_rev = collect_results(config.EXPERIMENTS_DATA+"results-{0}-ts-*rev.tsv".format(lang))
        regular_rev.to_csv(config.GENERATED_DATA+"generated-regular-bfs-{0}.csv".format(lang))
        regular_rev = None
        gc.collect()
        print "1"
        vernode_rev = collect_results(config.EXPERIMENTS_DATA+"results-ver-{0}-ts-*rev.tsv".format(lang),True)
        vernode_rev.to_csv(config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv".format(lang))
        vernode_rev = None
        gc.collect()
        print "2"
        regular = collect_results(config.EXPERIMENTS_DATA+"results-{0}-ts-*-orig.tsv".format(lang))
        regular.to_csv(config.GENERATED_DATA+"generated-regular-simulation-{0}.csv".format(lang))
        regular = None
        gc.collect()
        print "3"
        vernode = collect_results(config.EXPERIMENTS_DATA+"results-ver-{0}-ts-*-orig.tsv".format(lang),True)
        vernode.to_csv(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv".format(lang))
        vernode = None
        gc.collect()
        print "4"
        
        

