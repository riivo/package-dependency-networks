# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 22:49:26 2016

@author: Riivo
"""

import sys
import config
import matplotlib.pyplot as plt
import numpy  as np
import pandas as pd
import seaborn as sns
sns.set_context("paper")
sns.set_style("ticks")

from collections import defaultdict
current_pal = sns.color_palette()

#%%
def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = '%s%%' % n
    return percentile_


#%%
lang = "JS"
if len(sys.argv) > 1:
    lang = sys.argv[1]
    print "Got argument", "Rust"
    
adoption_file = config.FINAL_DATA+"cleaned_{0}_dependency_final.csv.gz"
release_file = config.FINAL_DATA+"cleaned_{0}_release_final.csv.gz"
opts = {"na_filter": False}
#%%

df_adoption =  pd.read_csv(adoption_file.format(lang), **opts)
df_release =  pd.read_csv(release_file.format(lang), **opts)

df_fixed = pd.read_csv(config.WORKING_DATA+"fixed_adopted_{0}_meta.csv".format(lang), sep="\t",**opts)
df_fixed.loc[pd.isnull(df_fixed.orig_ver_string), "orig_ver_string"] = ""

#%%
#print ((df_fixed.commit_ts-df_fixed.release_ts_y)/86400.0)

sub1 = df_fixed[df_fixed.release_ts_y > df_fixed.commit_ts]

print sub1.shape

#%%
print "\nLang", lang
uniq_dep = df_fixed[["project_name", "project_github"]].drop_duplicates()
uniq_dep_adopt = df_fixed[["adopted_name", "adopted_github"]].drop_duplicates().rename(columns={"adopted_name":"project_name", "adopted_github":"project_github"})


print "\nPublished projects", df_release.query("is_published==1")[["project_name", "project_github"]].drop_duplicates().shape
print "non-Published projects", df_release.query("is_published==0")[["project_name", "project_github"]].drop_duplicates().shape
print "\nadoption projects", df_adoption[["project_name", "project_github"]].drop_duplicates().shape
print "\nAll initial sample", pd.concat([df_adoption[["project_name", "project_github"]], df_release[["project_name", "project_github"]],uniq_dep_adopt]).drop_duplicates().shape


print "total projects net", pd.concat([uniq_dep, uniq_dep_adopt]).drop_duplicates().shape
print "unique adopted projects net", uniq_dep_adopt.shape
print "projects that have dependencies net", uniq_dep.shape

#%%
vers1 =  df_fixed[["project_name", "project_github", "project_ver", "adopted_name"]].groupby(["project_name", "project_github", "project_ver"]).agg({"adopted_name":lambda x: len(x.unique())}).reset_index()

print "\nversions with dependencies",vers1.shape

#%%
funcs =  [np.min, percentile(5), np.mean, np.median,percentile(95),np.max  ]
print "\ndependencies per version"
for fn in funcs:
    print fn.__name__, np.round(fn(vers1["adopted_name"].values),3)

#%%
print "\ndependency version changes",
vers1 =  df_fixed[["project_name", "project_github", "adopted_name", "adopted_ver"]].groupby(["project_name", "project_github", "adopted_name"]).agg({"adopted_ver":lambda x: len(x.unique())}).reset_index()

print "\nunique dependency versions, implcit"
for fn in funcs:
    print fn.__name__, np.round(fn(vers1["adopted_ver"].values),3)

vers1 =  df_fixed[["project_name", "project_github", "adopted_name", "orig_ver_string"]].groupby(["project_name", "project_github", "adopted_name"]).agg({"orig_ver_string":lambda x: len(x.unique())}).reset_index()

print "\nunique dependency versions, explitit"
for fn in funcs:
    print fn.__name__, np.round(fn(vers1["orig_ver_string"].values),3)

#%%


uniq_dep_adopt = df_fixed[["adopted_name", "adopted_github", "adopted_ver"]].drop_duplicates()

print "\ntotal project, versions ever adopted", uniq_dep_adopt.shape

print "\ntotal adoptions, vernode links", df_fixed.shape[0]



#

#%%
last_month = df_fixed.commit_ts.max() - 30 *86400
#print last_month
uniq_dep_adopt = df_fixed[df_fixed.commit_ts>= last_month][["adopted_name", "adopted_github", "adopted_ver"]].drop_duplicates()

print "\nversions active during last month", uniq_dep_adopt.shape