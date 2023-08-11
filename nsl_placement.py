"""
    This code allows to determine if an  NSLR (Network Slice Request)
    can be granted or not based on the available resources from the substrate
    several vnfs can be accepted in the same node
    
    23 oct 19:
    se adiciona funcion reduce_nslr_graph para reducir tamano del nslr graph

    04 nov 19:
    se adiciona fruncionalidad para poder mapear vnfs en nodos de otro tipo
    en caso de que los nodos del tipo necesario no tienen recursos disponibles;
    De esta forma, aceptar nslrs de un caso de uso tendra mayor influencia sobre
    la aceptacion de nslrs de otro caso de uso
"""

import copy
import logging
from operator import itemgetter

import networkx as nx

ranked_nodes_cpu = []
nsl_graph_red = {}  # reduced nsl graph


def nsl_placement(nslr, substrate):
    global ranked_nodes_cpu

    reduce_nslr_graph(nslr)  # builds a reduced version of the nsl_graph
    vnodes = nslr.nsl_graph_reduced["vnodes"]
    # print("*vnodes",vnodes)
    calculate_resource_potential(substrate, "cpu")
    nodes = copy.deepcopy(substrate.graph["nodes"])  # copy to temporarily work with it
    # ranked list of nodes by potential considering cpu and conections
    ranked_nodes_cpu = sort_nodes(nodes, "node_potential")

    ################### vnfs admission #################
    rejected = False
    already = []  # list of nodes that already hold a vnode
    for v in vnodes:
        if rejected:
            break
        for n in ranked_nodes_cpu:
            # if resource enough and node of the same type and node not used, vnode accepted
            if v["cpu"] <= n["cpu"] and v["type"] == n["type"] and n["id"] not in already:
                # mapping:
                v["mapped_to"] = n["id"]
                already.append(n["id"])
                break
            # insufficient resource, vnode rejected
            else:
                # slice rejection only when no node has enough resources
                if ranked_nodes_cpu.index(n) == len(
                        ranked_nodes_cpu) - 1:
                    rejected = True
                    break

    ################## vlinks admission #################
    if not rejected:
        rejected = analyze_links(nsl_graph_red, substrate)

    return rejected


def sort_nodes(node_list, sortby):
    sorted_list = sorted(node_list, key=itemgetter(sortby), reverse=True)  # sorted list
    return sorted_list


def calculate_resource_potential(substrate, resource_type):
    '''
        potential or importance of the node
        the potential of a node to embed vnfs in terms of cpu, str, and bw
        local_rsc_capacity  =  node resource * sumatoria de bw de todos los links adyacentes al nodo
        degree_centrality = degree/(n-1)
        node potential = local_rsc_capacity + degree_centrality
    '''

    nodes = substrate.graph["nodes"]
    links = substrate.graph["links"]
    for i in range(len(nodes)):
        bw_sum = 0

        for l in range(len(links)):
            if links[l]["source"] == i or links[l]["target"] == i:  # links connected to node i
                bw_sum += links[l]["bw"]  # sum of outgoing links bw

        local_rsc_capacity = nodes[i].get(resource_type) * bw_sum
        nodes[i]["node_potential"] = local_rsc_capacity


def reduce_nslr_graph(nslr):
    '''
        Procesamiento previo del nslr graph para reducir su tamano
        las vnfs que se puede intanciar en un mismo nodo fisico se agrupan como un unico nodo virtual
    '''
    centralized_vnfs = []
    edge_vnfs = []

    # 1. Group vnfs by node type:
    for vnf in nslr.nsl_graph["vnfs"]:  # loop vnfs
        if vnf["type"] == 0:
            centralized_vnfs.append(vnf)

        else:
            edge_vnfs.append(vnf)

            # 2. Sort the vnfs by backup:
    centralized_vnfs = sorted(centralized_vnfs, key=itemgetter("backup"))
    edge_vnfs = sorted(edge_vnfs, key=itemgetter("backup"))

    # 3. Group vnfs that will be instantiated in the same physical node:
    nsl_graph_red["vnodes"] = []
    group_vnfs(centralized_vnfs, 0)
    group_vnfs(edge_vnfs, 1)

    # 4. Create new vlinks considering the virtual nodes created
    nsl_graph_red["vlinks"] = []
    new_vlinks(nsl_graph_red, nslr.nsl_graph)

    # 5. resulting graph is added to the nslr
    nslr.set_nsl_graph_reduced(nsl_graph_red)


def group_vnfs(vnfs_list, node_type):
    '''
        creates different vnodes and adds them to the reduced graph
    '''

    vnode = dict
    vnode["vnfs"] = []  # ids of the vnfs that make up this vnode
    vnode["type"] = node_type

    if len(nsl_graph_red["vnodes"]) == 0:
        cont = 0
    else:
        cont = len(nsl_graph_red["vnodes"])

    for i in range(len(vnfs_list)):
        if i == 0:
            vnode["cpu"] = vnfs_list[i]["cpu"]
            vnode["vnfs"].append(vnfs_list[i]["id"])
            if i == len(vnfs_list) - 1:
                vnode["id"] = cont
                nsl_graph_red["vnodes"].append(vnode.copy())
                cont += 1

        elif vnfs_list[i]["backup"] == vnfs_list[i - 1]["backup"]:
            vnode["cpu"] += vnfs_list[i]["cpu"]
            vnode["vnfs"].append(vnfs_list[i]["id"])
            if i == len(vnfs_list) - 1:
                vnode["id"] = cont
                nsl_graph_red["vnodes"].append(vnode.copy())
                cont += 1

        else:
            vnode["id"] = cont
            nsl_graph_red["vnodes"].append(vnode.copy())
            cont += 1
            vnode["cpu"] = vnfs_list[i]["cpu"]
            vnode["vnfs"] = []
            vnode["vnfs"].append(vnfs_list[i]["id"])
            if i == len(vnfs_list) - 1:
                vnode["id"] = cont
                nsl_graph_red["vnodes"].append(vnode.copy())
                cont += 1


def new_vlinks(nsl_graph_red, nsl_graph):
    vnfs = nsl_graph["vnfs"]
    vnodes = nsl_graph_red["vnodes"]
    for vlink in nsl_graph["vlinks"]:
        source = next(vnf for vnf in vnfs if vnf["id"] == vlink["source"])
        target = next(vnf for vnf in vnfs if vnf["id"] == vlink["target"])
        # if src and target are of the same type and are from the same backup, then do nothing (vlink is not considered)
        if source["type"] == target["type"] and source["backup"] == target["backup"]:
            pass
        # otherwise vlink is considered, since the pair of vnfs are in different vnodes
        else:
            new_src = next(vnode for vnode in vnodes if source["id"] in vnode["vnfs"])
            new_tgt = next(vnode for vnode in vnodes if target["id"] in vnode["vnfs"])
            new_vlink = {"source": new_src["id"], "target": new_tgt["id"], "bw": vlink["bw"]}
            nsl_graph_red["vlinks"].append(new_vlink)


def analyze_links(nsl_graph, substrate):
    '''
    Toma la decision de aceptar o rechazar basado en shortest path
    Encuentra el camino mas corto y con bw suficiente en cada link para instanciar
    un v.link. Max num de hops permitido es 5
    Si no hay un camino con hops <= 5 y suficiente bw, el nslr es rechazado 
    '''

    G = nx.node_link_graph(substrate.graph)  # graph format
    # copy to temporarily work with it
    links = copy.deepcopy(substrate.graph["links"])
    reject = False
    max_hops = 5
    vlinks = nsl_graph["vlinks"]
    vnfs = nsl_graph["vnodes"]
    for vlink in vlinks:
        substrate_src = next(vnf["mapped_to"] for vnf in vnfs if vnf["id"] == vlink["source"])
        substrate_dst = next(vnf["mapped_to"] for vnf in vnfs if vnf["id"] == vlink["target"])
        logging.debug("\n***vlink:", vlink)
        # What to do with the vnfs that are instantiated on the same node? charge for vlink? how much?
        paths = nx.all_simple_paths(G, source=substrate_src, target=substrate_dst)
        path_list = [p for p in paths]
        path_list.sort(key=len)
        for path in path_list:
            # check if all the links in the path have sufficient resource
            enough = True
            logging.debug("*PATH:", path)
            if len(path) >= max_hops:
                reject = True
                break
            else:
                for l in range(len(path) - 1):

                    link = next(lk for lk in links if ((lk["source"] == path[l] and lk["target"] == path[l + 1]) or (
                            lk["source"] == path[l + 1] and lk["target"] == path[l])))

                    if vlink["bw"] <= link["bw"]:  # there is enough bw
                        link["bw"] -= vlink["bw"]  # resource is updated
                        # enough bw                       
                    else:  # not enough bw
                        enough = False

                if enough:
                    vlink["mapped_to"] = path  # if there was enough bw on each link of the path, it is mapped
                    break
                elif not enough and path_list.index(path) == len(path_list) - 1:
                    reject = True

        if reject:
            break

    return reject
