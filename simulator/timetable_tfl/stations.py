import requests
import json
import lines as l
import pyarrow.parquet as pq
import pyarrow.compute as pc
import pyarrow as pa
import networkx as nx
from networkx import DiGraph
import haversine as hs   
from haversine import Unit
import plotly.graph_objects as go


def get_timetable():
    trip_parquet_file_path = ".output/timetable2/trips.parquet"
    trips = pq.read_table(trip_parquet_file_path)
    return trips

def get_routes(timetable):  
    paths_as_lists = timetable["path"].to_pylist()
    
    # 2. Convert inner lists to tuples (which are hashable and preserve order)
    # 3. Use dict.fromkeys to get unique values while preserving the order 
    #    of the paths as they appeared in your table.
    unique_tuples = list(dict.fromkeys(tuple(path) for path in paths_as_lists if path is not None))
    
    # 4. Convert back to a PyArrow Array
    return pa.array(unique_tuples)

def get_unique_stations(timetable):
    return pc.unique(pc.list_flatten(timetable["path"]))

def get_stations(line:str):
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/StopPoints")
    return inbound.json()

def create_station(stations, r_inbound):
    for station in r_inbound:
        station_dict = {}
        id_station = station["stationNaptan"]
        station_dict["lat"] = station["lat"]
        station_dict["lon"] = station["lon"]
        station_dict["name"] = station["commonName"]
        stations[id_station] = station_dict

def get_distance(station, station_to):
    loc_station1 = (station["lat"],station["lon"])
    loc_station2 = (station_to["lat"],station_to["lon"])
    return hs.haversine(loc_station1,loc_station2,unit=Unit.KILOMETERS)

## use th timetable file to get the paths
## fetch the stations just to get the lat,long
## Since there will be already the order, it will just go through every distinct path and calculate the edge and add it to network.

def main():
    # Create the graph
    graph = nx.DiGraph()    
    
    # Get timetable and extract the routes available in the timetable
    timetable = get_timetable()
    routes = get_routes(timetable)

    # Extract unique stations from the paths and create its nodes
    unique_stations = get_unique_stations(timetable) 

    # Extract all stations using the london tfl api 
    stations = {}
    lines = l.get_lines()
    for line in lines:
        r_inbound = get_stations(line["name"])
        if len(r_inbound) == 0:
            continue
        save_station = create_station(stations,r_inbound)

    # Add station name to the graph
    for s in unique_stations:
        s_name = stations[str(s)]["name"]
        graph.add_node(s_name)

    edges_list = []
    for path in routes:
        for i in range(0,len(path)-1):
            s_from = str(path[i])
            s_to = str(path[i+1])
            station_from = stations[s_from]
            station_to = stations[s_to]
            weight = get_distance(station_from,station_to)
            edges_list.append([station_from["name"],station_to["name"],{"weight": weight}])
            
    # Create edges
    graph.add_edges_from(edges_list)
    # return graph
    
main()