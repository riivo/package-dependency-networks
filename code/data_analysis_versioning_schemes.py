import re
import pandas as pd
import numpy as np
from collections import Counter
import seaborn as sns
import config


reg_exact = re.compile(r'^[\=]{0,1}\d+(\.\d+)*([\-]{1}[a-zA-Z0-9]*)?')
reg_semantic = re.compile(r'^[~\^\=\>\<\s]{1,2}\d+(\.\d+)*([\-]{1}[a-zA-Z0-9]*)?')

def version_type(ver_):
    ver = ver_.strip().replace(" ", "")
    ver = ver.lstrip("v")
    if ver == "*":
        return "*"
    if ver == ">=0": #For Ruby
        return "*"

    if ver[0:2] == "~>":
        rem = ver[2:]
        parts = rem.split(".")
        if len(parts) == 3:
            return "caret"
        elif len(parts) == 2:
            return "tilde"
        else:
            return "range"

    if ver in ["git", "path", "dev-master"]:
        #return "git or path or dev-master"
        return "other"

    if "," in ver:
        part = ver.split(",")
        all1 = map(version_type, part)
        all1 = map(lambda x: x is not None, all1)
        if any(all1):
            return "range"
        return "other"

    if "||" in ver:
        part = ver.split("||")
        all1 = map(version_type, part)
        all1 = map(lambda x: x is not None, all1)
        if any(all1):
            return "range"
        return "other"

    if "|" in ver:
        part = ver.split("|")
        all1 = map(version_type, part)
        all1 = map(lambda x: x is not None, all1)
        if any(all1):
            return "range"
        return "other"

    m1 = reg_exact.match(ver)

    if m1 is not None and m1.group(0) is not None:
        return "exact"

    m2 = reg_semantic.match(ver)
    if m2 is not None and m2.group(0) is not None:
        if ver[0] == "^":
            return "caret"
        elif ver[0] =="~":
            return "tilde"
        return "range"
        #return "inexact"

    if len(ver.strip()) == 0:
        return "other"

    return "other"


def extract_versions(dfa):
    versions = dfa.orig_ver_string.values.tolist()
    fixed =  map(version_type, versions)
    dfa.loc[:,"version_type"] = fixed
    return fixed

if __name__ == "__main__":
    opts = {"na_filter": False}
    # %%

    titles = [("Rust",None), ("JS",0),("JS",1), ("Ruby", 0),("Ruby", 1)]
    projs = []

    for lang_ in titles:
        print lang_
        lang = lang_[0]
        df_fixed = pd.read_csv(config.WORKING_DATA+"fixed_adopted_{0}_meta.csv".format(lang), sep="\t", **opts)
        df_fixed.loc[pd.isnull(df_fixed.orig_ver_string), "orig_ver_string"] = ""
        if lang_[1] in [0,1]:
            df_fixed = df_fixed[df_fixed.is_published == lang_[1]]
        #print df_fixed.head()
        #print df_fixed.orig_ver_string.value_counts()
        projs.append(df_fixed)

    versions = []
    for ti, b in zip(titles, projs):
        print ti
        ver_ = extract_versions(b)
        versions.append(ver_)
        print b.query("version_type == 'range'").orig_ver_string.value_counts()

    counters = [Counter(c) for c in versions]

    rows = []
    rows2  = []
    for i, x in enumerate(counters):
        total = float(sum(x.values()))
        suffix = {1: " Repo", 0: " GH", None: ""}
        for k, v in x.items():
            rows.append([titles[i][0]+suffix[titles[i][1]], k, v, v / total])


    versioning_use = pd.DataFrame.from_records(rows, columns=["Ecosystem", "Type", "Count", "Percentage"])
    tbl = pd.pivot_table(versioning_use,values="Percentage",index="Ecosystem", columns="Type",aggfunc=np.sum).fillna(0)
    tbl2 = pd.pivot_table(versioning_use,values="Count",index="Ecosystem", columns="Type",aggfunc=np.sum).fillna(0)
    tbl2.to_csv(config.TABLES+"version_notation_stats.csv")
    print tbl
    print tbl.to_latex(float_format="%.3f")
