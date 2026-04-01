import graph as g
import pyarrow as pa
from pyarrow import Table
import pyarrow.parquet as pq
import os 
import networkx as nx
from collections import OrderedDict

def save_statistics(stats):
    schema = pa.schema([
        ("stat", pa.string()),
        ("stations", pa.list_(pa.string())),
        ("stations_name", pa.list_(pa.string())),
        ("values", pa.list_(pa.float64()))
    ])
    stats_table = Table.from_pylist(stats,schema)
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")
    if not os.path.exists(os.path.join(os.getcwd(), '.output/timetable_tfl')):
        os.mkdir(".output/timetable_tfl", mode=0o777, dir_fd=None)
    pq.write_table(stats_table,".output/timetable_tfl/stats.parquet")

def get_top_x_items(d, size):
    item = OrderedDict(sorted(d.items(),key=lambda item: item[1],reverse=True))
    top_items = list(item.items())
    return [x[0] for x in top_items[:size]], [x[1] for x in top_items[:size]]

def station_list_degree(size, graph: nx.graph.Graph):
    degree = dict(nx.degree(graph))
    return get_top_x_items(degree,size)

def station_list_betweenness(size, graph: nx.graph.Graph):
    betweenness_centrality = nx.betweenness_centrality(graph)
    return get_top_x_items(betweenness_centrality,size)

def station_list_closeness(size, graph: nx.graph.Graph):
    closeness = nx.closeness_centrality(graph)
    return get_top_x_items(closeness, size)

# def station_list_k_core(size, graph: nx.graph.Graph):
#     k_core = nx.k_core(graph)
#     core_val = nx.core_number(graph)
#     max_value = max(core_val.values())
#     print(max_value)
#     print(k_core.nodes)
#     # return get_top_x_items(k_core,size)

# def station_list_h_index(size, graph: nx.graph.Graph):
#     h_index = nx.h_i

def get_stations_names(station_list) -> list:
    stations = g.get_stations()
    names = []
    for s in station_list:
        print(stations[s]["name"])
        names.append(stations[s]["name"])
    return names

def create_stats(stats_list,name, top_items, values):
    stats_list.append({
        "stat": name,
        "stations":top_items,
        "stations_name": get_stations_names(top_items),
        "values": values
    })

def main():
    graph = g.main()
    full_graph_size = len(graph.nodes())
    size = round(full_graph_size*(10/100))
    stats = []
    top_betweeness, values =  station_list_betweenness(size=size,graph=graph)
    create_stats(stats,"betweeness", top_betweeness, values)
    top_degree, values = station_list_degree(size=size,graph=graph)
    create_stats(stats,"degree", top_degree, values)
    top_closeness, values = station_list_closeness(size=size,graph=graph)
    create_stats(stats,"closeness", top_closeness, values)
    # top_k_core, values = 
    # station_list_k_core(size=size,graph=graph)
    # create_stats(stats,"k_core", top_k_core, values)
    save_statistics(stats=stats)


if __name__ == "__main__":
    main()