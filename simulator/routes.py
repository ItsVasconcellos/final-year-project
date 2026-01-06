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
        print(count)
    return unique_routes

#TODO change the function name to something more adequate hahah 
def get_all_routes():
    routes = extract_unique_routes()
    sum = 0
    for route in routes.values():
        route["count"] = route["count"] / 3 
        if route["count"] == 0: 
            route["count"] = 1
        sum += route["count"]
    print(sum/len(routes))