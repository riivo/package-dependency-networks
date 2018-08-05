#include <iostream>
#include <map>
#include <fstream>
#include <stdint.h>
#include <cstdint>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <list>
#include <set>

#include <iterator>
#include <algorithm>
#include <string>
#include <tuple>
#include <queue>

using namespace std;

#include "common.h"
#include "csv.h"
#include "Snap.h"

const int RUN_LONG = 1;

const int WRITE_GRAPH_WCC = 1;

#define SPREADING_FIX 1

class DataN {
public:
    std::string projver, adoptedver, commit, release, origver, published;

    DataN(std::string projver, std::string adoptedver, std::string commit, std::string release, std::string origver,
            std::string published) {
        this->projver = projver;
        this->adoptedver = adoptedver;
        this->commit = commit;
        this->release = release;
        this->origver = origver;
        this->published = published;
    }

    bool operator<(const DataN& rhs) const {
        return std::tie(projver, adoptedver) < std::tie(rhs.projver, rhs.adoptedver);
    }

};
//FIXME global smell
unordered_map<std::string, bool> is_published;

//typedef TPair<TStr, TStr> NetworkNodeType;
typedef std::unordered_map<int, std::unordered_map<int, vector<DataN>>> EData;

typedef TStr NetworkNodeType;

typedef TVec<TTuple<TStr, 5>> NetworkEdgeType;
typedef TNodeNet<NetworkNodeType> NetworkType;
typedef TPt<NetworkType> PNetworkType;

typedef TStr NetworkNodeTypeVer;
typedef TPair<TStr, TStr> NetworkEdgeTypeVer;
typedef TNodeEDatNet<NetworkNodeTypeVer, NetworkEdgeTypeVer> NetworkTypeVer;
typedef TPt<NetworkTypeVer> PNetworkTypeVer;

std::string inline keygen(std::string name, std::string proj) {
    return name + "\t" + proj;
}

std::string inline keygen(std::string name, std::string proj, std::string ver) {
    return name + "\t" + proj + "\t" + ver;
}
std::string inline extract_name(std::string key) {
    vector<std::string> parts = split(key, '\t');
    return keygen(parts[0], parts[1]);
}

vector<int> get_time_slices_old() {
    int jan12010 = 1262304000;
    int jun52106 = 1465147955;
    vector<int> splits;
    int curr_date = jan12010 + 0;
    while (curr_date < jun52106) {
        curr_date += int(86400.0 * 30 * 3.0);
        splits.push_back(curr_date);
    }
    sort(splits.begin(), splits.end());
    reverse(splits.begin(), splits.end());
    return splits;
}

vector<int> get_time_slices(bool three_month = false) {

    if (three_month) {
        std::vector<int> threemonth( { /*1467331200,*/1459468800, 1451606400, 1443657600, 1435708800, 1427846400,
                1420070400, 1412121600, 1404172800, 1396310400, 1388534400, 1380585600, 1372636800, 1364774400,
                1356998400, 1349049600, 1341100800, 1333238400, 1325376000, 1317427200, 1309478400, 1301616000,
                1293840000, 1285891200, 1277942400, 1270080000, 1262304000, 1254355200, 1246406400, 1238544000,
                1230768000, 1222819200, 1214870400, 1207008000, 1199145600, 1191196800, 1183248000, 1175385600,
                1167609600, 1159660800, 1151712000, 1143849600, 1136073600, 1128124800, 1120176000, 1112313600,
                1104537600, 1096588800, 1088640000 });

        return threemonth;
    }

    std::vector<int> onemonth( { /*1467331200, 1464739200, 1462060800,*/1459468800, 1456790400, 1454284800, 1451606400,
            1448928000, 1446336000, 1443657600, 1441065600, 1438387200, 1435708800, 1433116800, 1430438400, 1427846400,
            1425168000, 1422748800, 1420070400, 1417392000, 1414800000, 1412121600, 1409529600, 1406851200, 1404172800,
            1401580800, 1398902400, 1396310400, 1393632000, 1391212800, 1388534400, 1385856000, 1383264000, 1380585600,
            1377993600, 1375315200, 1372636800, 1370044800, 1367366400, 1364774400, 1362096000, 1359676800, 1356998400,
            1354320000, 1351728000, 1349049600, 1346457600, 1343779200, 1341100800, 1338508800, 1335830400, 1333238400,
            1330560000, 1328054400, 1325376000, 1322697600, 1320105600, 1317427200, 1314835200, 1312156800, 1309478400,
            1306886400, 1304208000, 1301616000, 1298937600, 1296518400, 1293840000, 1291161600, 1288569600, 1285891200,
            1283299200, 1280620800, 1277942400, 1275350400, 1272672000, 1270080000, 1267401600, 1264982400, 1262304000,
            1259625600, 1257033600, 1254355200, 1251763200, 1249084800, 1246406400, 1243814400, 1241136000, 1238544000,
            1235865600, 1233446400, 1230768000, 1228089600, 1225497600, 1222819200, 1220227200, 1217548800, 1214870400,
            1212278400, 1209600000, 1207008000, 1204329600, 1201824000, 1199145600, 1196467200, 1193875200, 1191196800,
            1188604800, 1185926400, 1183248000, 1180656000, 1177977600, 1175385600, 1172707200, 1170288000, 1167609600,
            1164931200, 1162339200, 1159660800, 1157068800, 1154390400, 1151712000, 1149120000, 1146441600, 1143849600,
            1141171200, 1138752000, 1136073600, 1133395200, 1130803200, 1128124800, 1125532800, 1122854400, 1120176000,
            1117584000, 1114905600, 1112313600, 1109635200, 1107216000, 1104537600, 1101859200, 1099267200, 1096588800,
            1093996800, 1091318400, 1088640000 });

    return onemonth;
}
#ifdef SPREADING_FIX

std::string inline spkey(std::string key) {
    return key;
}
std::tuple<int, int, int, int, int> spreading(const PNetworkType& Graph, const int start_node, EData& reverse_storage,
        EData& storage, bool reverse = true) {
    typedef std::pair<int, std::unordered_set<std::string>> payload;
    unordered_map<int, int> visited;
    unordered_map<int, int> distances;
    unordered_set<std::string> unique;
    unordered_set<std::string> unique_published;

    long long size = 0;
    int max_depth = 0;
    std::queue<payload> current;

    distances[start_node] = 0;
    int first_level = 0;
    const int VISITED = 1337;
    visited[start_node] = VISITED;

    NetworkType::TNodeI Node = Graph->GetNI(start_node);
    if (reverse) {

        for (int e = 0; e < Node.GetInDeg(); e++) {
            const int innode = Node.GetInNId(e);
            std::unordered_set<std::string> vers;
            for (auto edgeload : reverse_storage[start_node][innode]) {
                vers.insert(edgeload.projver);

            }
            if (vers.size() > 0) {
                current.push(make_pair(innode, vers));
                distances[innode] = 1;
                max_depth = 1;
                visited[innode] = VISITED;
            }

        }
    } else {
        for (int e = 0; e < Node.GetOutDeg(); e++) {
            const int outnode = Node.GetOutNId(e);
            std::unordered_set<std::string> vers;
            for (auto edgeload : storage[start_node][outnode]) {
                vers.insert(edgeload.adoptedver);
            }
            if (vers.size() > 0) {
                current.push(make_pair(outnode, vers));
                distances[outnode] = 1;
                max_depth = 1;
                visited[outnode] = VISITED;
            }

        }
    }

    first_level = current.size();

    while (!current.empty()) {
        payload c = current.front();

        current.pop();

        const int curent_level_distance = distances[c.first];
        NetworkType::TNodeI InNode = Graph->GetNI(c.first);

        const int node_deg = reverse ? InNode.GetInDeg() : InNode.GetOutDeg();
        for (int e = 0; e < node_deg; e++) {

            const int innode = reverse ? InNode.GetInNId(e) : InNode.GetOutNId(e);
            if (visited[innode] != VISITED) {

                if (reverse) {
                    std::unordered_set<std::string> vers;
                    for (auto edgeload : reverse_storage[c.first][innode]) {
                        if (c.second.find(edgeload.adoptedver) != c.second.end()) {
                            vers.insert(edgeload.projver);
                        }
                    }
                    current.push(make_pair(innode, vers));
                } else {
                    std::unordered_set<std::string> vers;
                    for (auto edgeload : storage[c.first][innode]) {
                        if (c.second.find(edgeload.projver) != c.second.end()) {
                            vers.insert(edgeload.adoptedver);
                        }
                    }
                    current.push(make_pair(innode, vers));
                }
                auto ukey = Graph->GetNI(innode).GetDat().CStr();
                unique.insert(ukey);
                if (is_published[ukey])
                    unique_published.insert(ukey);

                distances[innode] = curent_level_distance + 1;
                max_depth = max(max_depth, curent_level_distance + 1);
                visited[innode] = VISITED;
            }
        }

        size++;
    }
    return make_tuple(size, max_depth, unique.size(), first_level, unique_published.size());

}

std::tuple<int, int, int, int, int> spreading(const PNetworkTypeVer& Graph, const int start_node,
        list<std::pair<int, string>>& all_versions, bool reverse = true) {
    //typedef std::pair<int, std::string> payload;
    unordered_set<string> visited;

    unordered_map<int, int> distances;
    unordered_set<std::string> unique;
    unordered_set<std::string> unique_published;

    long long size = 0;
    long long ghsize = 0;

    int max_depth = 0;
    std::queue<int> current;
    distances[start_node] = 0;
    current.push(start_node);

    const auto start_key = spkey(Graph->GetNI(start_node).GetDat().CStr());
    const auto start_project_name = extract_name(Graph->GetNI(start_node).GetDat().CStr());
    visited.insert(start_key);
    int first_level_degree = 0;
    while (!current.empty()) {
        int cur_level = current.front();

        current.pop();

        const int curent_level_distance = distances[cur_level];
        NetworkTypeVer::TNodeI InNode = Graph->GetNI(cur_level);

        const int degree_under = reverse ? InNode.GetInDeg() : InNode.GetOutDeg();
        for (int e = 0; e < degree_under; e++) {

            const int innode = reverse ? InNode.GetInNId(e) : InNode.GetOutNId(e);
            auto current_project_name = extract_name(Graph->GetNI(innode).GetDat().CStr());
            auto pkey = spkey(Graph->GetNI(innode).GetDat().CStr());

            if (visited.find(pkey) == visited.end() && current_project_name.compare(start_project_name) != 0) {

                all_versions.push_back(
                        pair<int, std::string>(curent_level_distance, Graph->GetNI(innode).GetDat().CStr()));
                current.push(innode);
                distances[innode] = curent_level_distance + 1;
                max_depth = max(max_depth, curent_level_distance + 1);

                visited.insert(pkey);
                //cout <<c << " " << InNode.GetDat().CStr() << " " << innode << " " <<  Graph->GetNI(innode).GetDat().CStr() << " " << ukey << std::endl;
                unique.insert(current_project_name);
                if (is_published[current_project_name]) {
                    unique_published.insert(current_project_name);
                }

            }
        }
        if (cur_level == start_node) {
            first_level_degree = unique.size() + 0;
        }

        size++;
    }
    return make_tuple(size - 1, max_depth, unique.size(), first_level_degree, unique_published.size());
}

#else
//FIXME
std::tuple<int, int, int, int, int> spreading_naive(const PNetworkType& Graph, const int start_node, EData& reverse_storage,
        EData& storage, bool reverse = true) {
    typedef std::pair<int, int> payload;
    unordered_map<int, int> visited;
    unordered_map<int, int> distances;
    unordered_set<std::string> unique;
    unordered_set<std::string> unique_published;

    long long size = 0;
    int max_depth = 0;
    std::queue<payload> current;
    current.push(make_pair(start_node, NULL));
    distances[start_node] = 0;
    int first_level = 0;

    first_level = current.size();

    const int VISITED = 1337;
    visited[start_node] = VISITED;
    while (!current.empty()) {
        payload c = current.front();

        current.pop();

        const int curent_level_distance = distances[c.first];
        NetworkType::TNodeI InNode = Graph->GetNI(c.first);

        const int node_deg = reverse ? InNode.GetInDeg() : InNode.GetOutDeg();
        for (int e = 0; e < node_deg; e++) {

            const int innode = reverse ? InNode.GetInNId(e) : InNode.GetOutNId(e);
            if (visited[innode] != VISITED) {

                current.push(make_pair(innode, NULL));
                auto ukey = Graph->GetNI(innode).GetDat().CStr();
                unique.insert(ukey);
                if (is_published[ukey])
                unique_published.insert(ukey);

                distances[innode] = curent_level_distance + 1;
                max_depth = max(max_depth, curent_level_distance + 1);
                visited[innode] = VISITED;
            }
        }

        size++;
    }
    return make_tuple(size - 1, max_depth, unique.size(), first_level, unique_published.size());

}

int uniq_degree(const PNetworkTypeVer& Graph, const int start_node, bool reverse = true) {
    unordered_set<std::string> unique;
    NetworkTypeVer::TNodeI InNode = Graph->GetNI(start_node);

    const int degree_under = reverse ? InNode.GetInDeg() : InNode.GetOutDeg();
    for (int e = 0; e < degree_under; e++) {

        const int innode = reverse ? InNode.GetInNId(e) : InNode.GetOutNId(e);
        auto ukey = extract_name(Graph->GetNI(innode).GetDat().CStr());
        unique.insert(ukey);

    }
    return unique.size();

}

std::tuple<int, int, int, int, int> spreading(const PNetworkTypeVer& Graph, const int start_node,
        list<std::pair<int, string>>& all_versions, bool reverse = true) {
    //typedef std::pair<int, std::string> payload;
    unordered_set<string> visited;

    unordered_map<int, int> distances;
    unordered_set<std::string> unique;
    unordered_set<std::string> unique_published;

    long long size = 0;
    int max_depth = 0;
    std::queue<int> current;
    distances[start_node] = 0;
    current.push(start_node);

    auto start_key = extract_name(Graph->GetNI(start_node).GetDat().CStr());
    visited.insert(start_key);
    int first_level_degree = 0;
    while (!current.empty()) {
        int cur_level = current.front();

        current.pop();

        const int curent_level_distance = distances[cur_level];
        NetworkTypeVer::TNodeI InNode = Graph->GetNI(cur_level);

        const int degree_under = reverse ? InNode.GetInDeg() : InNode.GetOutDeg();
        for (int e = 0; e < degree_under; e++) {

            const int innode = reverse ? InNode.GetInNId(e) : InNode.GetOutNId(e);
            auto ukey = extract_name(Graph->GetNI(innode).GetDat().CStr());
            all_versions.push_back(pair<int, std::string>(curent_level_distance, Graph->GetNI(innode).GetDat().CStr()));
            if (visited.find(ukey) == visited.end()) {

                current.push(innode);
                distances[innode] = curent_level_distance + 1;
                max_depth = max(max_depth, curent_level_distance + 1);

                visited.insert(ukey);
                //cout <<c << " " << InNode.GetDat().CStr() << " " << innode << " " <<  Graph->GetNI(innode).GetDat().CStr() << " " << ukey << std::endl;
                unique.insert(ukey);
                if (is_published[ukey]) {
                    unique_published.insert(ukey);
                }

            }
        }
        if (cur_level == start_node) {
            first_level_degree = unique.size();
        }

        size++;
    }
    return make_tuple(size, max_depth, unique.size(), first_level_degree, unique_published.size());

}
#endif

void run_parallel(const PNetworkType& Graph, EData& storage, EData& reverse_storage, std::string argname, bool reverse =
        true) {
    vector<int> nodes;
    const int node_count = Graph->GetNodes();
    nodes.reserve(node_count);

    for (NetworkType::TNodeI NI = Graph->BegNI(); NI < Graph->EndNI(); NI++) {
        nodes.push_back(NI.GetId());
    }
    long long counter = 0;
    std::random_shuffle(nodes.begin(), nodes.end());
    TIntFltH PRankH;

    bool isPR = false;
    if (!reverse) {
        isPR = true;
        TIntFltH HubH, AuthH;
        log(" PageRank... ");
        TSnap::GetPageRank(Graph, PRankH, 0.85, 1e-6, 100);
        cout << "pnodes " << PRankH.Len() << std::endl;
        cout << "vnodes " << nodes.size() << std::endl;
        cout << "gnodes " << Graph->GetNodes() << std::endl;

    }

    log("starting parallel");
    std::string rev = reverse ? "-orig" : "rev";
    ofstream out("results-" + argname + rev + ".tsv");
    for (int i = 0; i < node_count; i++) {

        counter += 1;
        if (counter % 10000 == 0) {
            log("done " + std::to_string(double(counter) / double(node_count)));
        }
        std::tuple<int, int, int, int, int> res = spreading(Graph, nodes[i], reverse_storage, storage, reverse);
        auto ndata = Graph->GetNI(nodes[i]);
        out << ndata.GetDat().CStr() << "\t" << std::get<0>(res) << "\t" << std::get<1>(res) << "\t" << std::get<2>(res)
                << "\t" << ndata.GetInDeg() << "\t" << ndata.GetOutDeg() << "\t" << std::get<3>(res) << "\t"
                << (isPR ? std::to_string(PRankH.GetDat(ndata.GetId())) : "") << "\t" << std::get<4>(res) << "\n";

    }
    out.flush();
    out.close();
}

void run_parallel(const PNetworkTypeVer& Graph, std::string argname, bool reverse = true) {
    vector<int> nodes;
    const int node_count = Graph->GetNodes();
    nodes.reserve(node_count);

    for (NetworkTypeVer::TNodeI NI = Graph->BegNI(); NI < Graph->EndNI(); NI++) {
        nodes.push_back(NI.GetId());
    }
    int counter = 0;
    std::random_shuffle(nodes.begin(), nodes.end());
    TIntFltH PRankH;

    bool isPR = false;
    if (!reverse) {
        isPR = true;
        log(" PageRank... ");

        //TSnap::GetPageRankMP(Graph, PRankH, 0.85);
        TSnap::GetPageRank(Graph, PRankH, 0.85, 1e-6, 100);
        cout << "pnodes " << PRankH.Len() << std::endl;
        cout << "vnodes " << nodes.size() << std::endl;
        cout << "gnodes " << Graph->GetNodes() << std::endl;

    }

    log("starting parallel");

    std::string rev = reverse ? "-orig" : "rev";
    ofstream out("results-ver-" + argname + rev + ".tsv");
    ofstream paths("paths-ver-" + argname + rev + ".tsv");
    for (int i = 0; i < node_count; i++) {
        std::list<std::pair<int, string>> all_versions;
        counter++;
        if (counter % 10000 == 0)
            log("donef " + std::to_string(double(counter) / double(node_count)));

        tuple<int, int, int, int, int> res = spreading(Graph, nodes[i], all_versions, reverse);

        auto ndata = Graph->GetNI(nodes[i]);
        out << ndata.GetDat().CStr() << "\t" << std::get<0>(res) << "\t" << std::get<1>(res) << "\t" << std::get<2>(res)
                << "\t" << ndata.GetInDeg() << "\t" << ndata.GetOutDeg() << "\t" << std::get<3>(res) << "\t"
                << (isPR ? std::to_string(PRankH.GetDat(ndata.GetId())) : "") << "\t" << std::get<4>(res) << "\n";

        if (isPR) {
            paths << ndata.GetDat().CStr();
            for (auto elem : all_versions) {
                paths << "," << elem.first << "\t" << elem.second;
            }
            paths << "\n";
        }

    }
    paths.close();

    out.flush();
    out.close();
}
template<class PGraph>
void PlotWccDistr(const PGraph& Graph, const TStr& FNmPref, TStr DescStr) {
    TIntPrV WccSzCnt;
    TSnap::GetWccSzCnt(Graph, WccSzCnt);
    if (DescStr.Empty()) {
        DescStr = FNmPref;
    }
    TGnuPlot GnuPlot("wcc." + FNmPref,
            TStr::Fmt("%s. G(%d, %d). Largest component has %f nodes", DescStr.CStr(), Graph->GetNodes(),
                    Graph->GetEdges(), WccSzCnt.Last().Val1 / double(Graph->GetNodes())));
    GnuPlot.AddPlot(WccSzCnt, gpwLinesPoints, "", "pt 6");
    GnuPlot.SetXYLabel("Size of weakly connected component", "Number of components");
    GnuPlot.SetScale(gpsLog10XY);
    GnuPlot.SavePng();
}

template<typename T>
void stats(const T& graph, EData* storage, bool vernode, int upperlimit = 0, ofstream* stats_file = NULL) {
    cout << "Stats" << endl;
    cout << "All nodes " << graph->GetNodes() << endl;
    cout << "All edges " << graph->GetEdges() << endl;

    int no_published = 0, no_github = 0;

    for (typename T::TObj::TNodeI NI = graph->BegNI(); NI < graph->EndNI(); NI++) {
        bool is_pub = false;
        if (vernode) {
            auto ukey = extract_name(NI.GetDat().CStr());
            is_pub = is_published[ukey];
        } else {
            is_pub = is_published[NI.GetDat().CStr()];
        }
        if (is_pub)
            no_published++;
        else
            no_github++;

    }

    cout << "Github nodes " << no_github << " repo" << no_published << endl;

    if (stats_file != NULL) {
        (*stats_file) << upperlimit << "\t" << graph->GetNodes() << "\t" << graph->GetEdges();
    }

    if (storage != NULL) {
        long long sum = 0;
        long long count = 0;
        long long uniq_uniq = 0;
        for (auto it = graph->BegEI(); it < graph->EndEI(); it++) {
            auto payload = (*storage)[it.GetSrcNId()][it.GetDstNId()];
            sum += payload.size();
            count += 1;

            set<DataN> s(payload.begin(), payload.end());
            uniq_uniq += s.size();

        }
        cout << "unique unique " << uniq_uniq << endl;
        cout << "unique  edges " << count << endl;
        cout << "total  edges " << sum << endl;
        if (stats_file != NULL) {
            (*stats_file) << "\t" << count << "\t" << sum << "\t" << uniq_uniq;
        }

    }
    if (stats_file != NULL) {
        (*stats_file) << "\t" << no_github << "\t" << no_published;
        (*stats_file) << "\n";
    }

}
template<class PGraph>
void SaveEdgeList(const PGraph& Graph, const TStr& OutFNm, const TStr& Desc) {
    FILE *F = fopen(OutFNm.CStr(), "wt");
    if (HasGraphFlag(typename PGraph::TObj, gfDirected)) {
        fprintf(F, "# Directed graph: %s \n", OutFNm.CStr());
    } else {
        fprintf(F, "# Undirected graph (each unordered pair of nodes is saved once): %s\n", OutFNm.CStr());
    }
    if (!Desc.Empty()) {
        fprintf(F, "# %s\n", Desc.CStr());
    }
    fprintf(F, "# Nodes: %d Edges: %d\n", Graph->GetNodes(), Graph->GetEdges());
    if (HasGraphFlag(typename PGraph::TObj, gfDirected)) {
        fprintf(F, "# FromNodeId\tToNodeId\n");
    } else {
        fprintf(F, "# NodeId\tNodeId\n");
    }
    for (typename PGraph::TObj::TEdgeI ei = Graph->BegEI(); ei < Graph->EndEI(); ei++) {
        fprintf(F, "%s\t%s\n", ei.GetSrcNDat().CStr(), ei.GetDstNDat().CStr());
    }
    fclose(F);
}

void evolution(const PNetworkType& graph, EData& storage, EData& reverse_storage, std::string argname) {
    vector<int> cutoffs = get_time_slices();
    ofstream stats_file(argname + "-stats-regular.tsv");
    for (int upperlimit : cutoffs) {
        cout << upperlimit << endl;

        for (NetworkType::TNodeI NI = graph->BegNI(); NI < graph->EndNI(); NI++) {

            //to_delete.insert(node_id);

            set<int> for_delete;
            for (int e = 0; e < NI.GetOutDeg(); e++) {

                const int innode = NI.GetOutNId(e);
                for (auto it = storage[NI.GetId()][innode].begin(); it != storage[NI.GetId()][innode].end();) {
                    int ts = atoi(it->commit.c_str());
                    if (ts > upperlimit) {
                        it = storage[NI.GetId()][innode].erase(it);
                    } else {
                        it++;
                    }
                }
                for (auto it = reverse_storage[innode][NI.GetId()].begin();
                        it != reverse_storage[innode][NI.GetId()].end();) {
                    int ts = atoi(it->commit.c_str());
                    if (ts > upperlimit) {
                        it = reverse_storage[innode][NI.GetId()].erase(it);
                    } else {
                        it++;
                    }
                }

                if (storage[NI.GetId()][innode].size() == 0) {
                    for_delete.insert(innode);
                }
            }

            for (auto to_del = for_delete.begin(); to_del != for_delete.end(); to_del++)
                graph->DelEdge(NI.GetId(), *to_del, true);

        }
        set<int> to_delete;
        for (NetworkType::TNodeI NI = graph->BegNI(); NI < graph->EndNI(); NI++) {

            if (NI.GetInDeg() == 0 && NI.GetOutDeg() == 0) {
                to_delete.insert(NI.GetId());
            }
        }
        for (int to_del : to_delete)
            graph->DelNode(to_del);

        if (graph->GetNodes() == 0)
            break;

        if (WRITE_GRAPH_WCC) {
            std::string wccname("wcc-regular-" + argname + "-ts-" + std::to_string(upperlimit));

            PlotWccDistr(graph, wccname.c_str(), "");
            std::string graphname("graph-regular-" + argname + "-ts-" + std::to_string(upperlimit) + ".tsv");

            SaveEdgeList(graph, graphname.c_str(), "");
        }

        if (RUN_LONG) {

            run_parallel(graph, storage, reverse_storage, argname + "-ts-" + std::to_string(upperlimit), true);
            run_parallel(graph, storage, reverse_storage, argname + "-ts-" + std::to_string(upperlimit), false);
        }

        stats<PNetworkType>(graph, &storage, false, upperlimit, &stats_file);
    }
    stats_file.close();

}

void evolution(const PNetworkTypeVer& graph, std::string argname) {
    vector<int> cutoffs = get_time_slices();
    ofstream stats_file(argname + "-stats-vernode.tsv");
    for (const int upperlimit : cutoffs) {
        cout << upperlimit << endl;

        for (NetworkTypeVer::TNodeI NI = graph->BegNI(); NI < graph->EndNI(); NI++) {

            //to_delete.insert(node_id);

            set<int> for_delete;
            for (int e = 0; e < NI.GetOutDeg(); e++) {

                const int innode = NI.GetOutNId(e);
                int commit = atoi(NI.GetOutEDat(e).Val1.CStr());
                int release = atoi(NI.GetOutEDat(e).Val2.CStr());
                if (commit > upperlimit || release > upperlimit)
                    for_delete.insert(innode);

            }

            for (auto to_del : for_delete)
                graph->DelEdge(NI.GetId(), to_del, true);

        }
        set<int> to_delete;
        for (NetworkTypeVer::TNodeI NI = graph->BegNI(); NI < graph->EndNI(); NI++) {

            if (NI.GetInDeg() == 0 && NI.GetOutDeg() == 0) {
                to_delete.insert(NI.GetId());
            }
        }
        for (int to_del : to_delete)
            graph->DelNode(to_del);

        if (graph->GetNodes() == 0)
            break;

        if (WRITE_GRAPH_WCC) {
            std::string wccname("wcc-vernode-" + argname + "-ts-" + std::to_string(upperlimit));
            PlotWccDistr(graph, wccname.c_str(), "");
            std::string graphname("graph-vernode-" + argname + "-ts-" + std::to_string(upperlimit) + ".tsv");
            SaveEdgeList(graph, graphname.c_str(), "");
        }

        if (RUN_LONG) {

            run_parallel(graph, argname + "-ts-" + std::to_string(upperlimit), true);
            run_parallel(graph, argname + "-ts-" + std::to_string(upperlimit), false);
        }
        stats<PNetworkTypeVer>(graph, NULL, true, upperlimit, &stats_file);

    }
    stats_file.close();

}

template<typename T, class P>
int inline addNode(const T& graph, std::string tup, std::unordered_map<std::string, int>& ids, int & counter) {

    auto it = ids.find(tup);
    if (it == ids.end()) {
        ids[tup] = counter;

        graph->AddNode(counter, P(tup.c_str()));
        counter += 1;
        return counter - 1;
    } else {
        return it->second;
    }

}

int main(int argc, char* argv[]) {
    srand(42);
    std::string fname("data/input.csv");
    std::string argname("default");
    bool RUN_VERNODE = true;
    if (argc >= 4) {
        fname = argv[1];
        argname = argv[2];
        RUN_VERNODE = atoi(argv[3]) > 0;
    }
    cout << "Filename: " << fname << endl;
    cout << "Argname: " << argname << endl;

    cout << "Running long experiments" << RUN_LONG << endl;

    if (RUN_VERNODE) {
        log("VERNODE experiments");
    } else {
        log("REGULAR experiments");
    }

    log("starting ...");
    PNetworkType graph = NetworkType::New();
    PNetworkTypeVer vergraph = NetworkTypeVer::New();

    io::CSVReader<11, io::trim_chars<' '>, io::no_quote_escape<'\t'>> in(fname);

    in.read_header(io::ignore_no_column, "project_github", "project_name", "commit_ts", "project_ver", "adopted_name",
            "orig_ver_string", "is_published", "release_ts_x", "adopted_ver", "adopted_github", "release_ts_y");

    std::string proj, name, commit, ver, adopted, orig, published, relase_ts_x, adoptedver, adopted_github, relase_ts_y;
    int counter = 0, counter2 = 0;
    std::unordered_map<std::string, int> ids;
    std::unordered_map<std::string, int> ids_ver;

    EData storage;
    EData reverse_storage;
    int rows_parsed = 0;
    while (in.read_row(proj, name, commit, ver, adopted, orig, published, relase_ts_x, adoptedver, adopted_github,
            relase_ts_y)) {
        is_published[keygen(proj, name)] = stoi(published) == 1;
        if (!RUN_VERNODE) {

            int a = addNode<PNetworkType, NetworkNodeType>(graph, keygen(proj, name), ids, counter);
            int b = addNode<PNetworkType, NetworkNodeType>(graph, keygen(adopted_github, adopted), ids, counter);
            if (!graph->IsEdge(a, b, true)) {
                graph->AddEdge(a, b);
            }
            auto d = DataN(ver, adoptedver, commit, relase_ts_y, orig, published);
            storage[a][b].push_back(d);
            reverse_storage[b][a].push_back(d);
        } else {
            int c1 = addNode<PNetworkTypeVer, NetworkNodeTypeVer>(vergraph, keygen(proj, name, ver), ids_ver, counter2);
            int c2 = addNode<PNetworkTypeVer, NetworkNodeTypeVer>(vergraph, keygen(adopted_github, adopted, adoptedver),
                    ids_ver, counter2);
            bool add_edge = true;
            if (vergraph->IsEdge(c1, c2)) {
                add_edge = false;
                auto edge_data = vergraph->GetEDat(c1, c2);

                if (atoi(commit.c_str()) < atoi(edge_data.Val1.CStr())) {
                    add_edge = true;
                }
            }
            if (add_edge) {
                vergraph->AddEdge(c1, c2, TPair<TStr, TStr>(commit.c_str(), relase_ts_y.c_str()));
            }
        }

        if (++rows_parsed % 100000 == 0) {
            log("done " + std::to_string(rows_parsed));
        }

    }

    if (RUN_VERNODE) {
        log("vernode experiments");
        cout << "Counter2" << counter2 << std::endl;
        stats<PNetworkTypeVer>(vergraph, NULL, true);
        run_parallel(vergraph, argname, true);
        run_parallel(vergraph, argname, false);
        evolution(vergraph, argname);

    } else {
        log("regular experiments");
        cout << "Counter" << counter << std::endl;
        stats<PNetworkType>(graph, &storage, false);

        log("start");
        run_parallel(graph, storage, reverse_storage, argname, true);
        run_parallel(graph, storage, reverse_storage, argname, false);

        log("end");
        evolution(graph, storage, reverse_storage, argname);
    }

    return EXIT_SUCCESS;
}

