import figure_params
import pandas as pd
import glob as glob
from matplotlib import pyplot as plt

#%%

def read_wcc(lang, gtype):
    folder = "../data/results_wcc/"
    files = glob.glob(folder+"wcc.wcc-{0}-{1}Exp-ts-*.tab".format(gtype,lang))
    res = []
    for f in files:
        ts = int(f.split("-")[-1][:-4])
        date = pd.to_datetime(ts, unit="s")
        data = pd.read_csv(f, sep="\t",comment="#", header=None, names=["csize", "ccount"])
        total = data.csize*data.ccount
        last = data.tail(1)
        biggest = last.csize * last.ccount*1.0
        wcc = biggest.sum() / total.sum()
        res.append([date, wcc])
    return  pd.DataFrame.from_records(res, columns=["date", "ratio"])
    
gtype = "vernode"
def last(df):
    return df.ratio.max()
    
for gtype in ["vernode", "regular"]:
    dfr  = read_wcc("Rust",gtype)
    dfjs  = read_wcc("JSCl",gtype)
    dfruby  = read_wcc("RubyCl",gtype)
    
    plt.figure()
    plt.plot(dfr.date, dfr.ratio, label = "Rust {0:.4f}".format(last(dfr)))
    plt.plot(dfjs.date, dfjs.ratio, label="JS {0:.4f}".format(last(dfjs)))
    plt.plot(dfruby.date, dfruby.ratio, label="Ruby {0:.4f}".format(last(dfruby)))
    #plt.yscale("log")
    plt.ylabel("Fraction of projects in LWCC")
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    figure_params.sns.despine()
    plt.savefig("../paper/figures/wccs/"+gtype+".pdf")
        
    
