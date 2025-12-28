import networkx as nx
import csv


def get_stations():
    stations_code_list = []
    stations_name_dict = {}
    with open(file="../database/stations.csv", mode='r') as stationsFile:
        stations = csv.DictReader(stationsFile)
        for station in stations:
            stations_code_list.append(station["code"]) 
            stations_name_dict[station["code"]] = station["name"]
    return stations_code_list, stations_name_dict

def get_routes():
    unique_routes = {}
    with open(file="../database/routes.tsv", mode='r') as routesFile:
        count = 0
        routes = csv.reader(routesFile, delimiter="\t")
        for route in routes:
            if unique_routes.get(''.join(route)):
                unique_routes[''.join(route)] += 1
                continue
            unique_routes[''.join(route)] = 1
            count+=1
    return unique_routes

def get_edges():
    edges_list = []
    with open(file="../database/edges.csv", mode='r') as connectionFile:
        edges = csv.DictReader(connectionFile)
        for edge in edges:
            edges_list.append([edge["source"],edge["target"],{"weight": edge["distance"]}])
    return edges_list

# def avg_value():
#     sum = 0
#     for route in unique_routes.items():
#         sum = sum + route[1]
#     avg = sum/len(unique_routes)
#     print(avg)

# def max_value():
#     station = ""
#     maximum = 0
#     for route in unique_routes.items():    
#         if route[1] >= int(maximum):
#             station = route[0]
#             maximum = route[1]
#     print(station)
#     print(maximum)

def create_graph():
    stations, _ = get_stations()
    edges = get_edges()
    graph = nx.DiGraph()
    for station in stations:
        graph.add_node(station)
    print(graph.number_of_nodes())
    print(len(edges))
    for edge in edges:
        source, target, weight = edge[0], edge[1], edge[2]
        graph.add_edge(u_of_edge=source, v_of_edge=target, **weight)
    print(graph.number_of_edges())

    return graph


def main():
    get_routes()
    railway_network = create_graph()

if __name__ == "__main__":
    main()