# This file contains the logic to populate edges and nodes in the graph of the webpage.
import json
from platform import node
import numpy as np
import pandas as pd
from storageNodeHandler import getStorageScriptFromStack
from networkNodeHandler import getInitiator, getInitiatorURL
from graphviz import Digraph
import networkx as nx
from networkx.drawing import nx_agraph
import pygraphviz


def convGraphToNX(file):
    return nx_agraph.from_agraph(pygraphviz.AGraph(file))


def dicToExcel(dict, path):
    df = pd.DataFrame(data=dict)
    df = df.T
    df.columns = [
        "script_name",
        "method_name",
        "label",
        "num_requests_sent",
        "num_nodes",
        "num_edges",
        "nodes_div_by_edges",
        "edges_div_by_nodes",
        "in_degree",
        "out_degree",
        "in_out_degree",
        "ancestor",
        "descendants",
        "closeness_centrality",
        "in_degree_centrality",
        "out_degree_centrality",
        "is_anonymous",
        "is_eval_or_external_function",
        "descendant_of_eval_or_function",
        "ascendant_script_has_eval_or_function",
        "num_script_successors",
        "num_script_predecessors",
        "storage_getter",
        "storage_setter",
        "cookie_getter",
        "cookie_setter",
        "getAttribute",
        "setAttribute",
        "addEventListener",
        "removeAttribute",
        "removeEventListener",
        "sendBeacon",
    ]
    df.to_excel(path)


def fileToCount(file, types, category):
    dic = {}
    for line in file:
        dataset = json.loads(line)
        script_url = getStorageScriptFromStack(dataset["stack"])
        if script_url not in dic:
            dic[script_url] = [0] * len(types)
        dic[script_url][types.index(dataset[category])] += 1
    return dic


def main():
    # methods = {id: ['script_name-0', 'method_name-1', 'label-2', 'num_requests_sent-3', 'num_node-4', 'num_edges-5', 'nodes_div_by_edges-6', 'edges_div_by_nodes-7', 'in_degree-8', 'out_degree-9', 'in_out_degree-10', 'ancestor-11', 'descendants-12',
    #                'closeness_centrality-13', 'in_degree_centrality-14', 'out_degree_centrality-15', 'is_anonymous-16', 'is_eval_or_external_function-17', 'descendant_of_eval_or_function-18', 'ascendant_script_has_eval_or_function-19','num_script_successors-20',
    #                'num_script_predecessors-21', 'storage_getter-22', 'storage_setter-23', 'cookie_getter-24', 'cookie_setter-25', "getAttribute-26", "setAttribute-27", "addEventListener-28",
    #                 "removeAttribute-29", "removeEventListener-30", "sendBeacon-31"]}
    methods = {}

    site = "dailymail.co.uk"
    folder = (
        "C:/Users/Hadiy/OneDrive/Desktop/webpage-crawler-extension/server/output/"
        + site
        + "/"
    )
    path = (
        "C:/Users/Hadiy/OneDrive/Desktop/webpage-crawler-extension/server/output/"
        + site
        + "/graph"
    )
    graph = convGraphToNX(path)

    pathtonodes = (
        "C:/Users/Hadiy/OneDrive/Desktop/webpage-crawler-extension/server/output/"
        + site
        + "/nodes.json"
    )
    # Opening JSON file
    f = open(pathtonodes)
    data = json.load(f)
    track = 0
    func = 0
    is_eval_or_external_function_ids = []
    script_ids = []
    for key in data.keys():

        if data[key][1] == "Script":
            script_ids.append(data[key][0])
            if key.split("@")[1] == "":
                is_eval_or_external_function_ids.append(data[key][0])

        if data[key][1] == "ScriptMethod" and key != "ScriptMethod@@":

            if data[key][0] not in methods.keys():
                methods[(data[key][0])] = [key.split("@")[1], key.split("@")[2]]

            # label as functional (label -> 0)
            if data[key][2] == 0 and data[key][3] != 0:
                methods[data[key][0]].append(0)
                func += data[key][3]
            # label as tracking (label -> 1)
            elif data[key][3] == 0 and data[key][2] != 0:
                methods[data[key][0]].append(1)
                track += data[key][2]
            # label mixed as tracking (label -> 1)
            elif data[key][2] != 0 and data[key][3] != 0:
                methods[data[key][0]].append(1)
            # label no initialization methods as functional (label -> 0)
            elif data[key][2] == 0 and data[key][3] == 0:
                methods[data[key][0]].append(0)
            # num_requests_sent
            methods[data[key][0]].append(data[key][2] + data[key][3])

    # num of nodes, edges, (n/e), and (e/n)
    num_edges = graph.number_of_edges()
    num_nodes = graph.number_of_nodes()
    nodes_div_by_edges = num_nodes / num_edges
    edges_div_by_nodes = num_edges / num_nodes

    for key in methods.keys():
        methods[key].append(num_nodes)
        methods[key].append(num_edges)
        methods[key].append(nodes_div_by_edges)
        methods[key].append(edges_div_by_nodes)

    # node ids from int to str
    method_ids = [str(i) for i in methods.keys()]
    # in-out degree
    out_degree = graph.out_degree(method_ids)
    in_degree = graph.in_degree(method_ids)

    for item in in_degree:
        methods[int(item[0])].append(item[1])
    for item in out_degree:
        methods[int(item[0])].append(item[1])

    in_degree_centrality = nx.in_degree_centrality(graph)
    out_degree_centrality = nx.out_degree_centrality(graph)

    for key in methods.keys():
        # sum of in-out degree
        methods[key].append(methods[key][8] + methods[key][9])
        # ancestors and desendants
        methods[key].append(len(nx.ancestors(graph, str(key))))
        methods[key].append(len(nx.descendants(graph, str(key))))
        # closeness_centrality
        methods[key].append(nx.closeness_centrality(graph, str(key)))
        # in_degree_centrality
        methods[key].append(in_degree_centrality[str(key)])
        # out_degree_centrality
        methods[key].append(out_degree_centrality[str(key)])
        # is_anonymous
        if methods[key][1] == "":
            methods[key].append(1)
        else:
            methods[key].append(0)
        # is_eval_or_external_function
        if methods[key][0] == "":
            methods[key].append(1)
        else:
            methods[key].append(0)

        # descendant_of_eval_or_function
        # ascendant_script_has_eval_or_function
        # num_script_successors
        # num_script_predecessors
        methods[key].append(0)
        methods[key].append(0)
        methods[key].append(0)
        methods[key].append(0)
        for node_id in nx.descendants(graph, str(key)):
            if int(node_id) in is_eval_or_external_function_ids:
                methods[key][18] = 1
            if int(node_id) in script_ids:
                methods[key][20] += 1
        for node_id in nx.ancestors(graph, str(key)):
            if int(node_id) in is_eval_or_external_function_ids:
                methods[key][19] = 1
            if int(node_id) in script_ids:
                methods[key][21] += 1

    # nodes = nx.closeness_centrality(graph)
    # print(nx.reciprocity(graph, method_ids))

    # 'storage_getter', 'storage_setter', 'cookie_getter', 'cookie_setter'
    with open(folder + "cookie_storage.json") as file:
        storage = fileToCount(
            file,
            ["storage_getter", "storage_setter", "cookie_getter", "cookie_setter"],
            "function",
        )
    for mthd in methods.keys():
        methods[mthd].append(0)
        methods[mthd].append(0)
        methods[mthd].append(0)
        methods[mthd].append(0)
        for key in storage.keys():
            if methods[mthd][0] + "@" + methods[mthd][1] == key:
                # ["storage_getter", "storage_setter", "cookie_getter", "cookie_setter"]
                methods[mthd][22] = storage[key][0]
                methods[mthd][23] = storage[key][1]
                methods[mthd][24] = storage[key][2]
                methods[mthd][25] = storage[key][3]

    # event getter
    with open(folder + "eventget.json") as file:
        storage = fileToCount(file, ["getAttribute"], "event")
    for mthd in methods.keys():
        methods[mthd].append(0)
        for key in storage.keys():
            if methods[mthd][0] + "@" + methods[mthd][1] == key:
                # ["getAttribute"]
                methods[mthd][26] = storage[key][0]

    # event setter
    with open(folder + "eventset.json") as file:
        storage = fileToCount(
            file,
            [
                "setAttribute",
                "addEventListener",
                "removeAttribute",
                "removeEventListener",
                "sendBeacon",
            ],
            "event",
        )
    for mthd in methods.keys():
        methods[mthd].append(0)
        methods[mthd].append(0)
        methods[mthd].append(0)
        methods[mthd].append(0)
        methods[mthd].append(0)
        for key in storage.keys():
            if methods[mthd][0] + "@" + methods[mthd][1] == key:
                # ["setAttribute", "addEventListener", "removeAttribute", "removeEventListener", "sendBeacon"]
                methods[mthd][27] = storage[key][0]
                methods[mthd][28] = storage[key][1]
                methods[mthd][29] = storage[key][2]
                methods[mthd][30] = storage[key][3]
                methods[mthd][31] = storage[key][4]

    dicToExcel(
        methods,
        "C:/Users/Hadiy/OneDrive/Desktop/webpage-crawler-extension/server/output/"
        + site
        + "/features.xlsx",
    )
    print(track, func)


main()
