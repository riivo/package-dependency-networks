# -*- coding: utf-8 -*-

import sys

import time

from scipy.stats import pearsonr

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy  as np
import pandas as pd
import seaborn as sns
import gc
sns.set_context("paper",font_scale=1.2)
sns.set_style("ticks")

current_pal = sns.color_palette()
import functools, logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

CACHE = {}

matplotlib.rcParams['pdf.fonttype'] = 42

palette = sns.color_palette("Paired")
UNIFIED_COLORS = {"JS":palette[1], "Ruby":palette[3], "Rust":palette[5]}

import config


class log_with(object):
    ENTRY_MESSAGE = 'Entering {}'
    EXIT_MESSAGE = 'Exiting {0}, took {1:.3f} s'

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, func):

        if not self.logger:
            logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
            #logging.basicConfig()
            self.logger = logging.getLogger(func.__module__)
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            namestr =  func.__name__+  ":"+ ', '.join('%s=%r' % entry for entry in zip(argnames,args) + kwds.items())
        
            self.logger.info(self.ENTRY_MESSAGE.format(namestr)) 
            time1 = time.time()
            f_result = func(*args, **kwds)
            time2 = time.time()
            self.logger.info(self.EXIT_MESSAGE.format(namestr,(time2-time1))) 
            return f_result
        return wrapper


LAST_MONTH="2016-04-01"
SINGLE_MONTH = "2016-04-01"
FILTER_POINT = "2016-04-01"
#%%
def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'p%s' % n
    return percentile_

def langf(lang, clean=True):
    return lang
    
    
@log_with()
def get_evo_data(lang="Rust"):
    lang = langf(lang)
    evolution = pd.read_csv(config.EXPERIMENTS_DATA+"{0}-stats-regular.tsv".format(lang),sep="\t",
                            skiprows=0,header=None,na_filter=False,  index_col=False,
                            names=["timestamp", "nodes","unique_relations","count", "version_relations", "unique", "github_nodes","published_nodes"])
    
    evolution["date"] = pd.to_datetime(evolution.timestamp,unit='s')
    evolution["date"] = pd.DatetimeIndex(evolution.date).normalize()
    evolution  = evolution[(evolution.nodes>0) & (evolution.date <= pd.to_datetime(FILTER_POINT)) ].sort_values("date")
    
    
    evolution_ver = pd.read_csv(config.EXPERIMENTS_DATA+"{0}-stats-vernode.tsv".format(lang),sep="\t",
                            skiprows=0,header=None,na_filter=False,  index_col=False,
                            names=["timestamp", "nodes","version_relations","github_nodes","published_nodes"])
    evolution_ver["date"] = pd.to_datetime(evolution_ver.timestamp,unit='s')
    evolution_ver["date"] = pd.DatetimeIndex(evolution_ver.date).normalize()
    evolution_ver  = evolution_ver[(evolution_ver.nodes>0)  & (evolution.date <= pd.to_datetime(FILTER_POINT)) ].sort_values("date")
    
    return evolution, evolution_ver

@log_with()
def rq2_evo1():    
    ev_rust, ev_ver_rust = get_evo_data("Rust")
    ev_js, ev_ver_js = get_evo_data("JS")
    ev_ruby, ev_ver_ruby = get_evo_data("Ruby")

    
    plt.figure(figsize=(5,4))

    sns.set_palette(sns.color_palette("Paired"))
    
    for plang in ["JS", "Ruby", "Rust"]:
        ev_js, ev_ver_js = get_evo_data(plang)
        res = plt.plot(ev_js.date, ev_js.nodes, label="{0} N".format(plang))
        plt.plot(ev_ver_js.date, ev_ver_js.nodes,":",c  = res[0].get_color(), label="{0} NV".format(plang))
        res = plt.plot(ev_js.date, ev_js.unique_relations, "-", label="{0} E".format(plang))
        plt.plot(ev_ver_js.date, ev_ver_js.version_relations,":",c  = res[0].get_color(), label="{0} EV".format(plang))
        

    plt.ylabel("Count")

    plt.yscale("log")
    plt.legend(loc="best",ncol=2)
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq2_evolution.pdf")


@log_with()
def rq2_evo_package_origin():
    ev_js, ev_ver_js = get_evo_data("JS")
    ev_ruby, ev_ver_ruby = get_evo_data("Ruby")

    plt.figure(figsize=(4, 3))

    sns.set_palette(sns.color_palette("Paired"))

    for plang in ["JS", "Ruby"]:
        ev_js, ev_ver_js = get_evo_data(plang)
        res = plt.plot(ev_js.date, ev_js.published_nodes, label="{0} Published".format(plang))
        plt.plot(ev_ver_js.date, ev_js.github_nodes, ":", c=res[0].get_color(), label="{0} GitHub".format(plang))

    plt.ylabel("Count")

    plt.yscale("log")
    plt.legend(loc="best", ncol=2)
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq2_evolution_published_gh.pdf")


#%%
@log_with()
def load_exp_data(filenamep, lang):
    filename = filenamep.format(langf(lang))
    if filename in CACHE:
        return CACHE[filename].copy()
    
    bfs1 = pd.read_csv(filename,na_filter=False)
    bfs1["date"] = pd.to_datetime(bfs1.date)
    bfs1 = bfs1[bfs1.date <= pd.to_datetime(FILTER_POINT)]
    CACHE[filename] = bfs1
    return bfs1.copy()


#%%
@log_with()
def basic_evo(dependencies=True,zeros_removed=True):
    suffix = ""
    if not zeros_removed:
        suffix = "_zeros_not_removed"    
        
    sns.set_palette(current_pal)
    plt.figure(figsize=(4,3))       
    title = "Average number of total dependencies"
    fname = "rq2_evolution_total_dependencies"+suffix+".pdf"    
    output = None
    if not dependencies:
        title = "Average number of total dependents"
        fname = "rq2_evolution_total_dependents"+suffix+".pdf"

    for lang in ["JS", "Ruby", "Rust"]:
        if dependencies:
            bfs1 = load_exp_data(config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv", lang)
            if zeros_removed:
                bfs1 = bfs1[bfs1.outdegree > 0]
        else:
            bfs1 = load_exp_data(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv", lang)
            if zeros_removed:
                bfs1 = bfs1[bfs1.indegree > 0]

            
        
            
        #vernode = pd.read_csv("../data/results/generated-vernode-simulation-{0}.csv".format(lang))

        rows = bfs1[["unique", "date"]].groupby("date").mean().reset_index()
        plt.plot(rows.date, rows.unique, label=lang, color=UNIFIED_COLORS[lang])
        rows["label"] = lang
        if output is None:
            output = rows[["unique","date","label"]].copy()
        else:
            output = pd.concat([output, rows[["unique","date","label"]].copy()])

        
        bfs1 = None
        rows = None
        gc.collect()
        
        
        
    plt.ylabel(title)       
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()        
    plt.savefig(config.FIGURES+fname)
    output.to_csv(config.FIGURES+fname+".csv")
    plt.close()


# %%
@log_with()
def basic_evo_graph(dependencies=True, zeros_removed=True):
    suffix = ""
    if not zeros_removed:
        suffix = "_zeros_not_removed"

    sns.set_palette(current_pal)
    plt.figure(figsize=(4, 3))
    title = "Average number of total dependencies"
    fname = "rq2_regular_evolution_total_dependencies" + suffix + ".pdf"
    output = None
    if not dependencies:
        title = "Average number of total dependents"
        fname = "rq2_regular_evolution_total_dependents" + suffix + ".pdf"

    for lang in ["JS", "Ruby", "Rust"]:
        if dependencies:
            bfs1 = load_exp_data(config.GENERATED_DATA+"generated-regular-bfs-{0}.csv", lang)
            if zeros_removed:
                bfs1 = bfs1[bfs1.outdegree > 0]
        else:
            bfs1 = load_exp_data(config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", lang)
            if zeros_removed:
                bfs1 = bfs1[bfs1.indegree > 0]

        # vernode = pd.read_csv("../data/results/generated-vernode-simulation-{0}.csv".format(lang))

        rows = bfs1[["unique", "date"]].groupby("date").mean().reset_index()
        plt.plot(rows.date, rows.unique, label=lang)
        rows["label"] = lang
        if output is None:
            output = rows[["unique", "date", "label"]].copy()
        else:
            output = pd.concat([output, rows[["unique", "date", "label"]].copy()])

        bfs1 = None
        rows = None
        gc.collect()

    plt.ylabel(title)
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+ fname)
    output.to_csv(config.FIGURES+ fname + ".csv")
    plt.close()



#%%
@log_with()
def dependency_correlation():
    queries = {
                "JS":"unique > 39000 or (uniq_degree > 5000)",
                "Ruby":"unique > 25000  or (uniq_degree > 5000)",
                "Rust":"unique > 1500 or (uniq_degree > 250)"
            }
    for lang in ["JS", "Ruby", "Rust"]:
        #regular = pd.read_csv("../data/results/generated-regular-simulation-{0}.csv".format(lang))
        bfs2 = load_exp_data(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv", lang)
        plt.figure(figsize=(3,3))
        
        ss = bfs2[(bfs2.date == pd.to_datetime(SINGLE_MONTH)) & (bfs2.indegree > 0)]
        #ss = bfs2[bfs2.indegree >= 0]
        plt.scatter(ss.uniq_degree, ss["unique"], color=UNIFIED_COLORS[lang], alpha=0.5,edgecolors='none',rasterized=True)
        plt.xlabel("Number of direct dependents")
        plt.ylabel("Total number of dependents")
        labels = ss.query(queries[lang])
        for _, x in labels.iterrows():

            plt.gca().annotate(x.project_name+" "+x.project_ver, (float(x.uniq_degree), float(x["unique"])),size=9)
            

        plt.gca().set_xlim(left=0)
        plt.gca().set_ylim(bottom=0)        
        sns.despine()
        plt.tight_layout(0.1)
        plt.savefig(config.FIGURES+"rq2_correlation_{0}.pdf".format(lang)) 
        plt.close() 
        print lang, " correlation", pearsonr(ss.uniq_degree, ss["unique"])
        


@log_with()
def dependency_correlation_project():
    queries = {
                "JS":"unique > 9000000 ",
                "Ruby":"(unique > 120000) or (indegree > 2000)",
                "Rust":"(unique > 3000) or (indegree > 600)"
            }

            
    for lang in ["JS", "Ruby", "Rust"]:
        #regular = pd.read_csv("../data/results/generated-regular-simulation-{0}.csv".format(lang))
        bfs2 = load_exp_data(config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", lang)
        bfs3 = load_exp_data(config.GENERATED_DATA+"generated-regular-bfs-{0}.csv", lang)
                
        plt.figure(figsize=(4,4))
        
        ss = bfs2[(bfs2.date == pd.to_datetime(SINGLE_MONTH)) & (bfs2.indegree > 0)]
        #ss = bfs2[bfs2.indegree >= 0]
        plt.scatter(ss.indegree, ss["unique"], alpha=0.5,edgecolors='none',rasterized=True)
        plt.xlabel("Number of direct dependents")
        plt.ylabel("Total number of dependents")
        labels = ss.query(queries[lang])
        for _, x in labels.iterrows():

            plt.gca().annotate(x.project_name, (float(x.indegree), float(x["unique"])),size=9)
            

        plt.gca().set_xlim(left=0)
        plt.gca().set_ylim(bottom=0)        
        sns.despine()
        plt.tight_layout(0.1)
        plt.savefig(config.FIGURES+"rq2_correlation_project_{0}.pdf".format(lang))
        plt.close() 
        print lang, " correlation", pearsonr(ss.uniq_degree, ss["unique"])            

#%%
@log_with()
def degree_evo(zeros_removed=True):    
    suffix = ""
    if not zeros_removed:
        suffix = "_zeros_not_removed"
    plt.figure(figsize=(4,3)) 
    sns.set_palette(sns.color_palette("Paired"))
    output = None
    for lang in ["JS", "Ruby", "Rust"]:
        #regular = pd.read_csv("../data/results/generated-regular-simulation-{0}.csv".format(lang))
        bfs1 = load_exp_data(config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv", lang)
            
        #vernode = pd.read_csv("../data/results/generated-vernode-simulation-{0}.csv".format(lang))

        p1 = bfs1[["indegree","outdegree", "date"]]
        if zeros_removed:
            p1 = p1.replace(0, np.nan)
            
        rows = p1.groupby("date").mean().reset_index()
        plt.plot(rows.date, rows.indegree, label="Dependents "+lang)
        plt.plot(rows.date, rows.outdegree, label="Dependencies "+lang)
        rows["label"] = lang
        if output is None:
            output = rows[["indegree","outdegree", "date","label"]].copy()
        else:
            output = pd.concat([output, rows[["indegree","outdegree", "date","label"]].copy()])

        p1 = None
        bfs1 = None
        rows = None
        gc.collect()       
    plt.ylabel("Average number of projects")       
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq2_evolution_degree"+suffix+".pdf")    
    output.to_csv(config.FIGURES+"rq2_evolution_degree"+suffix+".pdf.csv")   
    plt.close()

#%%
@log_with()
def degree_evo2(zeros_removed=True):    
    suffix = ""
    if not zeros_removed:
        suffix = "_zeros_not_removed"
    plt.figure(figsize=(4,3)) 
    sns.set_palette(sns.color_palette("Paired"))
    output = None
    for lang in ["JS", "Ruby", "Rust"]:
        bfs1 = load_exp_data(config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv", lang)    
        bfs2 = load_exp_data(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv", lang)

        p1 = bfs1[["indegree","outdegree","uniq_degree", "date"]]
        p2 = bfs2[["indegree","outdegree","uniq_degree", "date"]]
        if zeros_removed:
            p1 = p1.replace(0, np.nan)
            p2 = p2.replace(0, np.nan)
            
        rows = p1.groupby("date").mean().reset_index()
        rows2 = p2.groupby("date").mean().reset_index()
        
        plt.plot(rows2.date, rows2.uniq_degree, label="Dependents "+lang)
        plt.plot(rows.date, rows.uniq_degree, label="Dependencies "+lang)
        rows["label"] = lang
        if output is None:
            output = rows[["indegree","outdegree", "date","label"]].copy()
        else:
            output = pd.concat([output, rows[["indegree","outdegree", "date","label"]].copy()])

        p1 = None
        bfs1 = None
        rows = None
        gc.collect()       
    plt.ylabel("Average number of projects")       
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq2_evolution_degree_uq"+suffix+".pdf")    
    output.to_csv(config.FIGURES+"rq2_evolution_degree_uq"+suffix+".pdf.csv")    
    plt.close()
    
@log_with()
def vulnerability():
    sns.set_palette(sns.color_palette("Paired"))
    plt.figure(figsize=(4,3))       
    output = None
    for lang in ["JS", "Ruby", "Rust"]:
        bfs1 = load_exp_data(config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", lang)
        evodata = get_evo_data(lang)
        
        rows = bfs1[["unique", "date"]].groupby("date").agg([percentile(95), "max"]).reset_index()
        rows.columns = [''.join(col).strip() for col in rows.columns.values]
        rows = pd.merge(rows, evodata[0][["date","nodes"]], on="date", how="inner")
        plt.semilogy(rows.date, (rows.uniquep95)/(rows.nodes*1.0), label="90% "+lang)
        plt.semilogy(rows.date, rows.uniquemax/(rows.nodes*1.0), label="Max "+lang)

        rows.loc[:, "normalized_95p"] =  (rows.uniquep95) / (rows.nodes*1.0)
        rows.loc[:, "normalized_max"] =  rows.uniquemax / (rows.nodes * 1.0)
        rows["label"] = lang
        if output is None:
            output = rows.copy()
        else:
            output = pd.concat([output, rows.copy()])
        
        
        bfs1 = None

        rows = None
        gc.collect()            

    plt.ylabel("Vulnerability rate")
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq4_vulnerability_median.pdf")
    output.to_csv(config.FIGURES+"rq4_vulnerability_median.pdf"+".csv") 
    plt.close()

@log_with()
def vulnerability_distinguish():
    ##quantify vulnarbility effect on gihtub and npm
    sns.set_palette(sns.color_palette("Paired"))
    fig1 = plt.figure(figsize=(4, 3))
    ax1 = fig1.add_subplot(111)

    fig2 = plt.figure(figsize=(4,3))
    ax2 = fig2.add_subplot(111)

    output = None
    for lang in ["JS", "Ruby"]:
        bfs1 = load_exp_data(config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", lang)
        evodata = get_evo_data(lang)

        #"github_nodes", "published_nodes"]
        #"unique_published"]
        bfs1.loc[:,"unique_repo"] = bfs1.loc[:,"unique"] - bfs1.loc[:, "unique_published"]

        rows = bfs1[["unique_repo","unique_published","unique", "date"]].groupby("date").agg([percentile(95), "max","mean"]).reset_index()
        rows.columns = [''.join(col).strip() for col in rows.columns.values]
        rows = pd.merge(rows, evodata[0][["date", "nodes","github_nodes", "published_nodes"]], on="date", how="inner")
        res = ax1.plot(rows.date, rows.unique_repomax / (rows.github_nodes * 1.0), label="Application max " + lang)
        ax1.plot(rows.date, rows.unique_publishedmax / (rows.published_nodes * 1.0), label="Package max " + lang)
        ax1.plot(rows.date, rows.uniquemax / (rows.nodes * 1.0), label="Max " + lang, c  = res[0].get_color())

        ax2.plot(rows.date, rows.unique_repomean / (rows.github_nodes * 1.0), label="Application mean " + lang)
        ax2.plot(rows.date, rows.unique_publishedmean / (rows.published_nodes * 1.0), label="Package mean " + lang)


        rows["label"] = lang
        data_ = rows.copy()
        if output is None:
            output = data_
        else:
            output = pd.concat([output, data_])

        bfs1 = None

        rows = None
        gc.collect()

    ax1.set_ylabel("Vulnerability rate")

    ax1.legend(loc="best")
    fig1.tight_layout(pad=0.1)
    sns.despine(fig1)
    fig1.savefig(config.FIGURES+"rq4_vulnerability_dist_median.pdf")
    output.to_csv(config.FIGURES+"rq4_vulnerability_dist_median.pdf" + ".csv")


    ax2.set_ylabel("Vulnerability rate")

    ax2.legend(loc="best")
    fig2.tight_layout(pad=0.1)
    sns.despine(fig2)
    fig2.savefig(config.FIGURES+"rq4_vulnerability_dist_mean.pdf")
    plt.close()

@log_with()
def fragility():
    sns.set_palette(sns.color_palette("Paired"))
    plt.figure(figsize=(4,3))       
    output = None
    for lang in ["JS", "Ruby", "Rust"]:
        bfs1 = load_exp_data(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv", lang)
        evodata = get_evo_data(lang)
        
        rows = bfs1[["size", "date"]].groupby("date").agg([percentile(95), "max"]).reset_index()
        rows.columns = [''.join(col).strip() for col in rows.columns.values]
        rows = pd.merge(rows, evodata[1][["date","nodes"]], on="date", how="inner")
        plt.semilogy(rows.date, rows.sizep95/(rows.nodes*1.0), label="90% "+lang)
        plt.semilogy(rows.date, rows.sizemax/(rows.nodes*1.0), label="Max "+lang)

        rows["label"] = lang

        rows.loc[:, "normalized_95p"] = rows.sizep95/(rows.nodes*1.0)
        rows.loc[:, "normalized_max"] = rows.sizemax/(rows.nodes*1.0)

        data_ = rows
        if output is None:
            output = data_.copy()
        else:
            output = pd.concat([output, data_.copy()])
                
        bfs1 = None
        rows = None
        gc.collect()            

    plt.ylabel("Vulnerability rate")
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"rq4_fragility_median.pdf")
    plt.close()    
    output.to_csv(config.FIGURES+"rq4_fragility_median.pdf"+".csv") 

@log_with()
def distributionplot():
    sns.set_palette(current_pal)
    ds = [(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv","ver_sim","Dependents, k"),
          (config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", "reg_sim", "Dependents, k"),
          (config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv","ver_bfs","Dependencies, k"),
          (config.GENERATED_DATA+"generated-regular-bfs-{0}.csv", "reg_bfs","Dependencies, k")
          ]
    for lang in ["JS", "Ruby", "Rust"]:
        for dataset, label, xlabel in ds:
            
            bfs2 = load_exp_data(dataset, lang)
            bfs1 = bfs2[(bfs2.date == pd.to_datetime(SINGLE_MONTH))]
            counts = bfs1.unique.value_counts()
         
           
            plt.figure(figsize=(4,3))
            
            plt.loglog(counts.index+1, counts.values/(counts.values.sum()*1.0), "o")   
            plt.xlabel(xlabel)
            plt.ylabel("P(k)")       
            #plt.legend(loc="best")
            sns.despine()
            plt.tight_layout(0.1)
                    
            plt.savefig(config.FIGURES+"distribution_unique_{0}_{1}.pdf".format(lang, label)) 
            plt.close()             
            
@log_with()
def degree():
    sns.set_palette(current_pal)
    ds = [
          (config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv","ver_bfs","Dependencies, k"),
          (config.GENERATED_DATA+"generated-regular-bfs-{0}.csv", "reg_bfs","Dependencies, k")
          ]
    for lang in ["JS", "Ruby", "Rust"]:
        for dataset, label, xlabel in ds:
            
            bfs2 = load_exp_data(dataset, lang)
            bfs1 = bfs2[(bfs2.date == pd.to_datetime(SINGLE_MONTH))]
            indegree = bfs1.indegree.value_counts()
            outdegree = bfs1.outdegree.value_counts()
         
           
            plt.figure(figsize=(4,3))
            
            plt.loglog(indegree.index+1, indegree.values/(indegree.values.sum()*1.0), "o", alpha=0.5, label="Dependents")   
            plt.loglog(outdegree.index+1, outdegree.values/(outdegree.values.sum()*1.0), "s",alpha=0.5,label="Dependencies")   
                        
            plt.xlabel("Projects, k")
            plt.ylabel("P(k)")       
            plt.legend(loc="best")
            sns.despine()
            plt.tight_layout(0.1)
            plt.savefig(config.FIGURES+"distribution_degree_{0}_{1}.pdf".format(lang, label))         
            plt.close()            

@log_with()
def transitive_overlap():
    sns.set_palette(sns.color_palette("Paired"))
    palette =  sns.color_palette("Paired")
    colors = [palette[1], palette[3], palette[5]]
    langs = ["JS", "Ruby","Rust"]
    dfs = [pd.read_csv(config.GENERATED_DATA+"agg_path_{0}.csv".format(x), usecols=range(1, 6)) for x in langs]

    for i in range(3):
        dfs[i].loc[:, "binmultiple"] = (dfs[i].multiple > 0) + 0
        dfs[i].loc[:, "binconflicts"] = (dfs[i].conflicts > 0) + 0

        # print dfs[i].head()
    plt.figure(figsize=(4, 3))

    for p_, df, color_ in zip(langs, dfs, colors):
        p = p_.rstrip("Cl")

        rates = df.groupby("date")[["binmultiple", "binconflicts"]].mean().reset_index()
        plt.plot(pd.to_datetime(rates.date), rates.binmultiple, label=p, color=color_)  # +" Multiple")
        # plt.plot(pd.to_datetime(rates.date), rates.binconflicts, "--",label=p+" Conflicts")

    plt.ylabel("Dependency overlap rate")
    plt.legend(loc="best")
    plt.tight_layout(0.1)
    sns.despine()
    plt.savefig(config.FIGURES+"overlap_rate.pdf")
    plt.close()

@log_with()
def extract_latest_data():

    def load_ds(dataset, lang_):
        bfs2 = load_exp_data(dataset, lang_)
        bfs1 = bfs2[(bfs2.date == pd.to_datetime(LAST_MONTH))].copy()
        bfs1.drop("Unnamed: 0", axis=1, inplace=True)
        return bfs1

    """
    names_ = ["project_github", "project_name", "size", "max_depth", "unique", "indegree", "outdegree", "uniq_degree",
              "pagerank", "unique_published"]
    if ver:
        names_ = ["project_github", "project_name", "project_ver", "size", "max_depth", "unique", "indegree",
                  "outdegree", "uniq_degree", "pagerank", "unique_published"]
    """
    ds = [(config.GENERATED_DATA+"generated-vernode-simulation-{0}.csv", "ver_sim", "Dependents, k"),
          (config.GENERATED_DATA+"generated-regular-simulation-{0}.csv", "reg_sim", "Dependents, k"),
          (config.GENERATED_DATA+"generated-vernode-bfs-{0}.csv", "ver_bfs", "Dependencies, k"),
          (config.GENERATED_DATA+"generated-regular-bfs-{0}.csv", "reg_bfs", "Dependencies, k")
          ]

    outgoing = {
            "size":"dependencies_all",
            "max_depth":"depenencies_depth",
            "unique":"dependencies_unique",
            "uniq_degree":"dependencies_unique_direct",
            "unique_published":"dependencies_unique_published"
    }
    incoming = {
            "size":"dependents_all",
            "max_depth":"dependents_depth",
            "unique":"dependents_unique",
            "uniq_degree":"dependents_unique_direct",
            "unique_published":"dependents_unique_published"
    }
    vers = []
    regs = []
    for lang in ("Rust", "JS", "Ruby"):
        ver_bfs = load_ds(ds[2][0], lang)
        ver_sim = load_ds(ds[0][0], lang)

        ver_bfs.rename(columns=outgoing,inplace=True)
        ver_sim.rename(columns=incoming, inplace=True)
        print ver_bfs.shape
        print ver_sim.shape
        for c in ["pagerank","indegree","outdegree"]:
            ver_sim.drop(c, axis=1, inplace=True)


        ver_all = pd.merge(ver_bfs, ver_sim, on=["project_github", "project_name","project_ver","date"], how="inner")
        ver_all.loc[:,"lang"] = lang
        print ver_all.shape

        vers.append(ver_all)
        reg_bfs = load_ds(ds[3][0], lang)
        reg_sim = load_ds(ds[1][0], lang)

        for c in ["pagerank", "indegree", "outdegree"]:
            reg_sim.drop(c, axis=1, inplace=True)

        print reg_bfs.shape
        print reg_sim.shape

        reg_bfs.rename(columns=outgoing, inplace=True)
        reg_sim.rename(columns=incoming, inplace=True)

        reg_all = pd.merge(reg_bfs, reg_sim, on=["project_github", "project_name", "date"], how="inner")
        reg_all.loc[:,"lang"] = lang
        regs.append(reg_all)
        print reg_all.shape

    pd.concat(regs).to_csv(config.FIGURES+"last_month_data_reg.csv.gz", index=None, compression="gzip")
    pd.concat(vers).to_csv(config.FIGURES+"last_month_data_ver.csv.gz", index=None, compression="gzip")



#%%
if __name__ == "__main__":


    run_all = False
    if len(sys.argv) > 1:
        run_all = True

    print "RUN ALL", run_all

    extract_latest_data()
    dependency_correlation()
    transitive_overlap()
    basic_evo(True, True)
    vulnerability_distinguish()
    rq2_evo1()


    if run_all:
        rq2_evo_package_origin()

        vulnerability_distinguish()
        fragility()
        vulnerability()

        transitive_overlap()

        rq2_evo1()

        dependency_correlation_project()
        dependency_correlation()

        degree()
        distributionplot()

        basic_evo_graph(True, False)
        basic_evo_graph(True, False)

        basic_evo(True,True)
        basic_evo(False,True)
        basic_evo(True,False)
        basic_evo(False,False)


        degree_evo(True)
        degree_evo(False)

        degree_evo2(True)
        degree_evo2(False)


    
    

