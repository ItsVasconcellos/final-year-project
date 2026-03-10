import requests
import json
import lines as l
def get_routes_inbound(line: str):
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/Route/Sequence/all")
    return inbound.json()

def get_stations(routes):
    # There is always one objected expected
    if routes == None:
        return []
    if routes.get("stations"):
        for r in routes["stations"]:
            r["lines"] = []
        return routes["stations"] 
    return []

if __name__ == "__main__":
    stations = []
    routes = []
    lines = l.get_lines()
    for line in lines:
        r_inbound = get_routes_inbound(line["name"])
        stations += get_stations(r_inbound)
        break
    
    # create_edges(stations)
    for station in stations:
        print(station)
