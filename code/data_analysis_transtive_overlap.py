#calculate overal in first level dependecies and transtivie chains

import pandas as pd
import glob
from collections import defaultdict

import sys
import random
import config 

def load_paths(fname, unique = lambda x:(x[1],x[2])):
    fp = open(fname)
    data = []
    for line in fp:
        line = line.strip().split(",")
        start = line[0].split("\t")
        chain = map(lambda x:x.split("\t"), line[1:])
        #print start
        #print chain
        first_level = set([])
        transtive_level = set([])
        projs = defaultdict(set)
        projs_lv = defaultdict(set)
        
        max_level = 0
        for x in chain:
            if not x[0].isdigit():
                #print "FAIL", x
                continue
            lvl = int(x[0])
            max_level = max(lvl, max_level)
            if lvl == 0:
                first_level.add(unique(x))
            else:
                transtive_level.add(unique(x))
            projs[unique(x)].add(x[3])
            projs_lv[unique(x)].add(lvl)
            
        conflicts = sum(map(lambda x:len(x) > 1, projs.values()))
        multiple = sum(map(lambda x:len(x) > 1, projs_lv.values()))
        
        overlap = len(first_level.intersection(transtive_level))
        data.append([max_level, overlap, conflicts, multiple])
        
    return data

def collect(fname):
        ts = fname.split("-")[-1][:-7]
        ts = int(ts)
        results = load_paths(fname)
        df = pd.DataFrame.from_records(results, 
                                       columns  = ["depth", "intersection", "conflicts","multiple"])
        df.loc[:, "date"] = pd.to_datetime(ts, unit="s")
        return df


if __name__ == "__main__":
    lang = "Rust"
    if len(sys.argv) > 1:
        lang = sys.argv[1]
    print lang
        
    files = glob.glob(config.EXPERIMENTS_DATA+"/paths-ver-{0}-ts-*rev.tsv".format(lang))
    random.shuffle(files)
    print "Files", len(files)    
    summary =  [collect(i) for i in files]
    summary = pd.concat(summary)    
    summary.to_csv(config.GENERATED_DATA+"agg_path_{0}.csv".format(lang))

    


