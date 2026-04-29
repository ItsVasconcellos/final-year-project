import pyarrow.parquet as pq
import pyarrow as pa
import networkx as nx
import haversine as hs   
from haversine import Unit

def get_timetable():
    trip_parquet_file_path = ".output/timetable_tfl/trips.parquet"
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

def get_unique_stations(routes):
    stations = {}
    for r in routes:
        for s in r:
            if stations.get(s):
                continue
            stations[s] = 1
    return stations

def get_stations():
    stations_parque_file_path = ".output/timetable_tfl/stations.parquet"
    stations = pq.read_table(stations_parque_file_path).to_pylist()
    stations = {str(s["id"]): s for s in stations}
    return stations

def match_stations(all_stations, timetable_stations):
    stations = {}
    for s in timetable_stations:
        s = str(s)
        station = all_stations.get(s)
        stations[s] = station
    return stations

def get_distance(station, station_to):
    loc_station1 = (station["lat"],station["lon"])
    loc_station2 = (station_to["lat"],station_to["lon"])
    return hs.haversine(loc_station1,loc_station2,unit=Unit.KILOMETERS)

## use th timetable file to get the paths
## fetch the stations just to get the lat,long
## Since there will be already the order, it will just go through every distinct path and calculate the edge and add it to network.

def main():
    # Create the graph
    graph = nx.graph.Graph() 
    
    # Get timetable and extract the routes available in the timetable
    timetable = get_timetable()
    routes = get_routes(timetable)

    # Extract unique stations from the paths and create its nodes
    timetable_stations = get_unique_stations(routes) 
    # print(len(paths))
    all_stations = get_stations()

    stations_used = match_stations(all_stations=all_stations, timetable_stations=timetable_stations)

    # Add station name to the graph
    for s in stations_used:
        s_name = stations_used[str(s)]["name"]
        graph.add_node(s_name)

    edges_list = []
    for path in routes:
        for i in range(0,len(path)-1):
            s_from = str(path[i])
            s_to = str(path[i+1])
            if s_from == s_to:
                # print("self loop from " + str(s_from) + " to" + str(s_to))
                continue
            station_from = stations_used[s_from]
            station_to = stations_used[s_to]
            weight = get_distance(station_from,station_to)
            edges_list.append([station_from["name"],station_to["name"],{"weight": weight}])
            
    # Create edges
    graph.add_edges_from(edges_list)
    # return graph
    return graph
