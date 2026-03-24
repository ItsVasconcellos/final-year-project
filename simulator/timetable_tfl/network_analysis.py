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
    ])
    stats_table = Table.from_pylist(stats,schema)
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")
    if not os.path.exists(os.path.join(os.getcwd(), '.output/timetable_tfl')):
        os.mkdir(".output/timetable_tfl", mode=0o777, dir_fd=None)
    pq.write_table(stats_table,".output/timetable_tfl/stations.parquet")

def get_top_x_items(d, size):
    item = OrderedDict(sorted(d.items(),key=lambda item: item[1],reverse=True))
    top_items = [item for item in item.keys()]
    return top_items[:size]


def station_list_degree(size, graph: nx.graph.Graph):
    degree = dict(nx.degree(graph))
    return get_top_x_items(degree,size)

def station_list_betweenness(size, graph: nx.graph.Graph):
    betweenness_centrality = nx.betweenness_centrality(graph)
    return get_top_x_items(betweenness_centrality,size)

def station_list_closeness(size, graph: nx.graph.Graph):
    closeness = nx.closeness_centrality(graph)
    return get_top_x_items(closeness, size)

def main():
    graph = g.main()
    full_graph_size = len(graph.nodes())
    size = round(full_graph_size*(10/100))
    stats = []
    stats_betweeness = {
        "stat": "betweenness",
        "stations": station_list_betweenness(size=size,graph=graph)
    }
    stats.append(stats_betweeness)
    stats_degree = {
        "stat": "degree",
        "stations": station_list_degree(size=size,graph=graph)
    }
    stats.append(stats_degree)
    stats_closeness = {
        "stat": "closeness",
        "stations": station_list_closeness(size=size,graph=graph)
    }
    stats.append(stats_closeness)
    save_statistics(stats=stats)


if __name__ == "__main__":
    main()