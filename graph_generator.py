"""
-If a graph is connected then edges >= n-1
-If a graph has more than (n-1)(n-2)/2 edges, then it is connected.
#G = nx.gnm_random_graph(n,(2*n)-1) # a graph is chosen uniformly at random from the set of all graphs with n nodes and m edges
barabasi_albert_graph returns a random graph according to the Barabasi-Albert preferential attachment model
A graph of n nodes is grown by attaching new nodes each with m edges that are preferentially attached to existing nodes with high degree. 1 <= m < n
"""
import json
import os
import random
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

matplotlib.use("agg")

# cpu range for centralized nodes, a tuple is used which is an immutable obj
cpu_central = (300, 300)

cpu_edge = (100, 100)  # storage range for edge nodes
bw_range = (50, 50)  # bandwidth range

lista_dos = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 50
# lista_uno = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]#35
lista_cero = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 17
lista = lista_dos + lista_cero


def ba_graph(name, n):
    print("***")
    # n:Number of nodes m:Number of edges to attach from a new node to existing nodes
    g = nx.barabasi_albert_graph(n, 2)

    g.graph["min_cpu_cost"] = 0  # min cost possible in a time unit
    g.graph["max_cpu_revenue"] = 0  # max revenue possible in a time unit
    g.graph["edge_cpu"] = 0
    g.graph["centralized_cpu"] = 0
    g.graph["min_bw_cost"] = 0
    g.graph["max_bw_revenue"] = 0
    # capacities (cpu,str) are added to nodes randomly considering the intervals above:
    # random.seed(n)
    for n in g.nodes():
        node_type = random.choice(lista)
        print("node type:", node_type)
        g.nodes[n]["type"] = node_type

        if node_type == 1:
            g.nodes[n]["cpu"] = random.randint(cpu_edge[0], cpu_edge[1])
            g.graph["edge_cpu"] += g.nodes[n]["cpu"]
            g.graph["min_cpu_cost"] += g.nodes[n]["cpu"] * 3
            g.graph["max_cpu_revenue"] += g.nodes[n]["cpu"] * 6

        else:
            g.nodes[n]["cpu"] = random.randint(cpu_central[0], cpu_central[1])
            g.graph["centralized_cpu"] += g.nodes[n]["cpu"]
            g.graph["min_cpu_cost"] += g.nodes[n]["cpu"] * 1
            g.graph["max_cpu_revenue"] += g.nodes[n]["cpu"] * 2

    # max_cpu_profit in a time unit
    g.graph["max_cpu_profit"] = g.graph["max_cpu_revenue"] - g.graph["min_cpu_cost"]

    for l in g.edges():
        g.edges[l]["bw"] = random.randint(bw_range[0], bw_range[1])
        g.graph["min_bw_cost"] += g.edges[l]["bw"] * 0.5
        g.graph["max_bw_revenue"] += g.edges[l]["bw"] * 0.5 * 5 * 1.5

    g.graph["max_bw_profit"] = g.graph["max_bw_revenue"] - g.graph["min_bw_cost"]

    nx.draw(g, with_labels=True, font_weight='bold')
    my_path = os.path.abspath(__file__)
    today = datetime.today().strftime('%Y-%m-%d')
    plt.savefig(my_path + "/outputs/" + "graph_" + name + "_" + today + ".png")  # save as png
    plt.close()

    g_nl_format = nx.node_link_data(g)  # returns the graph in a node-link format

    my_path = os.path.abspath(__file__)
    with open(my_path + "/outputs/" + name + '.json', 'w') as json_file:
        json.dump(g_nl_format, json_file)
    return g_nl_format

    # return substrate ##quitarrrr


topo = ba_graph("10", 10)
