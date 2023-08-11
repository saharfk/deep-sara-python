def calculate_profit_nodes(nslr, end_simulation_time):
    # Calculates profit per time unit and then multiplies it by the nslr op. time
    cost = 0
    revenue = 0
    vnfs = nslr.nsl_graph_reduced["vnodes"]

    cf_cpu = 0  # cost factor of physical nodes(depends on node type)
    for vnf in vnfs:
        if vnf["type"] == 0:  # central
            cf_cpu = 1
        elif vnf["type"] == 1:  # edge
            cf_cpu = 3
        # else:
        #     cf_cpu = 4 
        cost += vnf["cpu"] * cf_cpu
        revenue += vnf["cpu"] * cf_cpu * 2  # revenue is twice the cost (so far)

    if nslr.end_time > end_simulation_time:
        # if it is greater, the portion of time until the end of the simulation is considered
        time = nslr.operation_time - (nslr.end_time - end_simulation_time)
    else:
        time = nslr.operation_time

    profit = (revenue - cost) * time
    return profit


def calculate_profit_links(nslr, end_simulation_time):
    # Calculates profit per time unit and then multiplies it by the nslr op. time
    cost = 0
    revenue = 0
    vlinks = nslr.nsl_graph_reduced["vlinks"]
    cf_bw = 0.5  # cost factor of physical links

    for vlink in vlinks:
        try:
            hops = len(vlink["mapped_to"]) - 1
        except KeyError:
            hops = 0
        cost += vlink["bw"] * cf_bw * hops  # cost is proportional to the number of hops
        revenue += vlink[
                       "bw"] * cf_bw * 5 * 1.5
        # (5: charged considering the maximum number of hops allowed and 1.5: an additional 50% to the cost with 5hops)

    if nslr.end_time > end_simulation_time:
        # if it is greater, the portion of time until the end of the simulation is considered
        time = nslr.operation_time - (nslr.end_time - end_simulation_time)
    else:
        time = nslr.operation_time

    profit = (revenue - cost) * time
    return profit


def calculate_request_utilization(nslr, end_simulation_time, substrate):
    vnfs = nslr.nsl_graph_reduced["vnodes"]
    vlinks = nslr.nsl_graph_reduced["vlinks"]
    central_sum = 0
    edge_sum = 0
    bw_sum = 0

    for vnf in vnfs:
        if vnf["type"] == 0:  # central
            central_sum += vnf["cpu"]
        elif vnf["type"] == 1:  # edge
            edge_sum += vnf["cpu"]

    for vlink in vlinks:
        bw_sum += vlink["bw"]

    if nslr.end_time > end_simulation_time:
        # if it is greater, the portion of time until the end of the simulation is considered
        time = nslr.operation_time - (nslr.end_time - end_simulation_time)
    else:
        time = nslr.operation_time

    edge_utl = edge_sum * time
    central_utl = central_sum * time
    links_utl = bw_sum * time

    return edge_utl, central_utl, links_utl