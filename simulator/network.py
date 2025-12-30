import networkx as nx
from networkx import DiGraph
import csv
def get_stations() -> tuple[list,dict]:
    stations_code_list = []
    stations_name_dict = {}
    with open(file="../database/stations.csv", mode='r') as stationsFile:
        stations = csv.DictReader(stationsFile)
        for station in stations:
            stations_code_list.append(station["code"]) 
            stations_name_dict[station["name"]] = station["code"]
    return stations_code_list, stations_name_dict


def get_edges() -> list:
    edges_list = []
    with open(file="../database/edges.csv", mode='r') as connectionFile:
        edges = csv.DictReader(connectionFile)
        for edge in edges:
            edges_list.append([edge["source"],edge["target"],{"weight": edge["distance"]}])
    return edges_list

def create_graph() -> DiGraph:
    stations, _ = get_stations()
    edges = get_edges()
    graph = nx.DiGraph()
    for station in stations:
        graph.add_node(station)
    for edge in edges:
        source, target, weight = edge[0], edge[1], edge[2]
        graph.add_edge(u_of_edge=source, v_of_edge=target, **weight)

    return graph

