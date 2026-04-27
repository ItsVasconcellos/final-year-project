import csv
import simulator.network_uk_railway.network as ntw

def extract_unique_routes():
    unique_routes = {}
    with open(file="../database/routes.tsv", mode='r') as routesFile:
        count = 0
        routes = csv.reader(routesFile, delimiter="\t")
        for route in routes:
            key = ''.join(route)
            if unique_routes.get(key):
                unique_routes[key]["count"] += 1 
                continue
            unique_routes[key] = {"count":1, "path": route}
            count+=1
        print("Unique routes:" + str(count))
    return unique_routes

def get_all_routes():
    """
    This function returns all the routes available, using extract_unique_routes and normalize the count.
    This is necessary since the routes are on a 3 day frequency.
    """
    routes = extract_unique_routes()
    # sum = 0
    for route in routes.values():
        route["count"] = int(route["count"] / 3)
        if route["count"] == 0: 
            route["count"] = 1
        # sum += route["count"]
    # Average route usage per day
    # print(sum/len(routes))
    return routes

def get_all_routes_and_distances():
    """
    This function returns the routes, with their respectives distances in KM, using the information in the dataset of edges.
    Some routes were removed since their total distance was equal to 0.
    This happened because the stations and consequently their edge and the did not exist in Stations.csv and Edges.tsv files. 
    """
    stations = ntw.get_edges_weight_dict()
    routes = get_all_routes()
    for route in routes.values():
        total_route_distance = 0 
        for i in range(0,len(route["path"])-1):
            key = route["path"][i] + "," + route["path"][i+1]
            if stations.get(key):
                total_route_distance += stations[key]
        total_route_distance  = round(total_route_distance,2)
        route["totalDistance"] = total_route_distance
    return routes 

get_all_routes_and_distances()