import csv

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