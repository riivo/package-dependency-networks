import logging
import re
import sys

import networkx as nx
import pandas as pd
import semantic_version

import config
import utils
from utils import chunks

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def read_graph(name):
    opts = {"na_filter": False}

    adoption_file = config.FINAL_DATA + "cleaned_{0}_dependency_final.csv.gz"
    release_file = config.FINAL_DATA + "cleaned_{0}_release_final.csv.gz"

    dfa_rust = pd.read_csv(adoption_file.format(name), **opts)
    dfr_rust = pd.read_csv(release_file.format(name), **opts)
    return dfa_rust, dfr_rust


def info(G, n=None):
    """Print short summary of information for the graph G or the node n.

    Parameters
    ----------
    G : Networkx graph
       A graph
    n : node (any hashable)
       A node in the graph G
    """
    info = ''  # append this all to a string
    if n is None:
        info += "Name: %s\n" % G.name
        type_name = [type(G).__name__]
        info += "Type: %s\n" % ",".join(type_name)
        info += "Number of nodes: %d\n" % G.number_of_nodes()
        info += "Number of edges: %d\n" % G.number_of_edges()
        nnodes = G.number_of_nodes()
        if len(G) > 0:
            if G.is_directed():
                indeg = filter(lambda x: x != 0, G.in_degree().values())
                outdeg = filter(lambda x: x != 0, G.out_degree().values())
                info += "Average in degree: %8.4f\n" % \
                        (sum(indeg) / float(len(indeg)))
                info += "Average out degree: %8.4f" % \
                        (sum(outdeg) / float(len(outdeg)))
            else:
                s = sum(G.degree().values())
                info += "Average degree: %8.4f" % \
                        (float(s) / float(nnodes))

    else:
        if n not in G:
            raise nx.NetworkXError("node %s not in graph" % (n,))
        info += "Node % s has the following properties:\n" % n
        info += "Degree: %d\n" % G.degree(n)
        info += "Neighbors: "
        info += ' '.join(str(nbr) for nbr in G.neighbors(n))
    return info


def compose_temporal_network(data, reverse=False):
    pass


def compose_network_meta(data, reverse=False):
    """nodes are proejcts, edges have annotations for which version the transition is valid list((src_ver, dst_ver))
    """
    net = nx.DiGraph()
    groups = data.groupby(["project_name", "adopted_name"])
    for (project_name, adopted_name), rows_ in groups:
        versions = rows_[["project_ver", "adopted_ver", "commit_ts"]].to_records(index=False).tolist()
        if reverse is False:
            version_dict = [(k, v, ts) for k, v, ts in versions]
            net.add_edge(project_name, adopted_name, data=version_dict)
        else:
            version_dict = [(v, k, ts) for k, v, ts in versions]
            net.add_edge(adopted_name, project_name, data=version_dict)

    return net


def compose_network_multi(data):
    """Multiple edges between nodes, each have data={src_ver:, dst:ver}
    """
    net = nx.MultiDiGraph()
    for row_ in data.iterrows():
        row = row_[1]
        net.add_edge(row.project_name, row.adopted_name, data={"src_ver": row.project_ver, "dst_ver": row.adopted_ver})
    return net


def compose_network_vernode(data, reverse=False):
    """ Every node is is (node, ver), single edge between nodes
    """

    net = nx.DiGraph()
    for row_ in data.iterrows():
        row = row_[1]
        if reverse is False:
            net.add_edge((row.project_name, row.project_ver), (row.adopted_name, row.adopted_ver),
                         timestamp=row.commit_ts)
        else:
            net.add_edge((row.adopted_name, row.adopted_ver), (row.project_name, row.project_ver),
                         timestamp=row.commit_ts)

    return net


def resolve_dependencies(npm_rel_):
    releases = {}
    groups = npm_rel_.groupby("project_name")  # "project_github",
    for proj, data in groups:

        vers2 = []
        for ver_, release_ts_ in data[["project_ver", "release_ts"]].to_records(index=False).tolist():
            try:
                vers2.append((release_ts_, semantic_version.Version(ver_)))
            except ValueError, e:
                print "Invalid release version", ver_
        releases[proj] = vers2
    return releases


def fix_project_wrapper(listing, releases):
    res = []

    for name, adopted_ver, commit_ts, vers2_ in listing:
        if vers2_ is not None:
            res.append(fix_project(name, adopted_ver, commit_ts, vers2_))
    return res


def fix_semver(inp):
    gr = re.search("([0-9][<>])", inp)
    if gr is not None:
        return inp[:gr.start() + 1] + "," + inp[gr.start() + 1:]

    return inp


def fix_project(name, adopted_ver, commit_ts, vers2):
    default_val = (name, "")

    matches = set([])
    for verx_ in adopted_ver.replace(" ", "").split("||"):

        try:
            fixed = None
            fixed = fix_semver(verx_)
            if fixed.find(",") == -1:
                fixed = utils.fix_semantic_x(fixed)
            spec = semantic_version.Spec(fixed)
            matches_ = [j for j in vers2 if spec.match(j[1])]
            matches.update(matches_)
        except (ValueError, TypeError), e:
            # print "Failed to parse", adopted_ver, fixed
            # print "fix_projext:214", e
            continue

    matches = list(matches)
    if len(matches) == 0:
        return default_val

    first = filter(lambda z: z[0] <= commit_ts, matches)
    first = sorted(first, key=lambda x: x[0], reverse=True)

    if len(first) == 0:
        # first = matche[0][1]
        return default_val
    else:
        first = first[0][1]

    return name, str(first)

    # dataset.loc[name,"fixed_version"] = str(first)


def fix_version_parallel(dataset_, releases):
    # inexact_releases[pd.isnull(inexact_releases.release_ts)]
    # SHOULD only fix those that do not have exact match
    dataset = dataset_.copy()
    logging.info("copy done")
    dataset.loc[:, "fixed_version"] = dataset.loc[:, "adopted_ver"]

    subset = dataset[pd.isnull(dataset.release_ts)].copy()
    logging.info("extract rows")
    logging.warn("FIXME")
    # input_data = [(name, x.adopted_ver, x.commit_ts, releases[x.adopted_name])
    #              for name, x in subset.iterrows()  if x.adopted_name in releases]
    # input_data = [(name, x.adopted_ver, x.commit_ts, x.adopted_name) for name, x in subset.iterrows()]

    subset.loc[:, 'adopted_replace'] = subset.loc[:, 'adopted_name'].apply(lambda x: releases.get(x, None))

    input_data = subset[["adopted_ver", "commit_ts", "adopted_replace"]].to_records()

    logging.info("starting parallel")
    results = [fix_project_wrapper(chnk, None) for chnk in chunks(input_data, 3000)]

    logging.info("parallel done")
    values = []
    idx = []
    for level in results:
        for k, v in level:
            values.append(v)
            idx.append(k)
    logging.info("results collected")
    dataset.loc[idx, "fixed_version"] = values
    return dataset


def main(lang_name):
    npm_dep, npm_rel_all = read_graph(lang_name)

    npm_rel = npm_rel_all.query("is_published==1").copy()

    print npm_rel.shape
    print npm_rel.groupby(["project_ver", "project_name"]).first().reset_index().shape

    ISRUBY = "new_ver" in npm_dep.columns

    if not ISRUBY:
        logging.info("NON Ruby, default action")
        adoptions_ = npm_rel[["project_name", "project_ver", "release_ts"]].rename(
            columns={"project_name": "adopted_name", "project_ver": "adopted_ver"})

        print npm_dep.shape
        inexact_releases = pd.merge(npm_dep, adoptions_, how="left", on=["adopted_name", "adopted_ver"])

        logging.info("starting to resolve dependencies")
        release_ver_dict = resolve_dependencies(npm_rel)

        print inexact_releases.shape
        logging.info("starting to fix semantic version")
        fixed_adopt = fix_version_parallel(inexact_releases, release_ver_dict)
        fixed_adopted_subset = fixed_adopt.query("fixed_version != ''")
        print "after fixed null", fixed_adopted_subset.shape

        fixed_adopted_subset = fixed_adopted_subset.rename(columns={"adopted_ver": "orig_ver_string"}).rename(
            columns={"fixed_version": "adopted_ver"})
        print fixed_adopted_subset.shape

    else:
        logging.info("Ruby, assuming version resolution has been done")
        print npm_dep.shape
        fixed_adopted_subset = npm_dep.query("new_ver != ''").rename(columns={"adopted_ver": "orig_ver_string"}).rename(
            columns={"new_ver": "adopted_ver"})
        if "scope" in fixed_adopted_subset.columns:
            fixed_adopted_subset.drop('scope', axis=1, inplace=True)

        print fixed_adopted_subset.shape

    adoptions_repos = npm_rel[["project_github", "project_name", "project_ver", "release_ts"]].rename(
        columns={"project_name": "adopted_name", "project_ver": "adopted_ver", "project_github": "adopted_github"})

    fixed_adopted_subset = pd.merge(fixed_adopted_subset, adoptions_repos, how="inner",
                                    on=["adopted_name", "adopted_ver"])
    print "after merge null", fixed_adopted_subset.shape
    # fixed_adopted_subset.loc[:,"project_ver "] = fixed_adopted_subset.project_ver.map(lambda x:x.strip())
    # fixed_adopted_subset = fixed_adopted_subset[~pd.isnull(fixed_adopted_subset.project_ver)].query("project_ver != ''")
    print "after projver null", fixed_adopted_subset.shape

    if ISRUBY:
        fixed_adopted_subset.loc[:, "release_ts_x"] = fixed_adopted_subset['release_ts']
        fixed_adopted_subset.rename(columns={"release_ts": "release_ts_y"}, inplace=True)

    print fixed_adopted_subset.shape
    colorder = ["project_github", "project_name", "commit_ts", "project_ver", "adopted_name",
                "orig_ver_string", "is_published", "release_ts_x", "adopted_ver", "adopted_github", "release_ts_y"]
    fixed_adopted_subset = fixed_adopted_subset[colorder]
    fixed_adopted_subset.to_csv("./working/fixed_adopted_{0}_meta.csv".format(lang_name), sep="\t", index=False,
                                encoding='utf-8')
    # fixed_adopted_subset.to_csv("./working//fixed_adopted_{0}_meta.csv2".format(lang_name), index=False, encoding='utf-8')
    logging.info("done")
    """
    logging.info("composing networks")

    graph = compose_network_meta(fixed_adopted_subset)
    #multigraph = compose_network_multi(fixed_adopted_subset)


    vernode = compose_network_vernode(fixed_adopted_subset)
    
    rev_graph = compose_network_meta(fixed_adopted_subset, True)
    rev_vernode = compose_network_vernode(fixed_adopted_subset, True)

    logging.info("writing graphs")

    nx.write_gpickle(graph, "./working/{0}_meta.gpickle".format(lang_name))
    nx.write_gpickle(vernode, "./working/{0}_vernode.gpickle".format(lang_name))
    nx.write_gpickle(rev_graph, "./working/{0}_meta_rev.gpickle".format(lang_name))
    nx.write_gpickle(rev_vernode, "./working/{0}_vernode_rev.gpickle".format(lang_name))
    """

# %%
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage <program>: Language"
        sys.exit(0)
    main(sys.argv[1])
