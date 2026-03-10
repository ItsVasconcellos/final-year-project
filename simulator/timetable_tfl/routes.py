import requests
import lines as l
import logging as log

def get_all_routes(line: str):
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/Route")
    return inbound.json()

def get_line_list():
    lines = l.get_lines()
    lines_id = ""
    for line in lines:
        lines_id += line["name"] + ","
    return lines_id[:-1]

def extract_routes(req):
    # There is always one objected expected
    routes = {}
    if req == None:
        return []
    for item in req:
        key = item["name"]
        print(key)
        routes[key] = [] 
        if not item.get("routeSections"):
            log.warning("Line found does not contain any active route")
            continue
        for r in item["routeSections"]:
            origin = r["originator"]
            destination = r["destination"]
            direction = r["direction"]
            routes[key].append([origin,destination,direction])
    return routes

def main():
    lines = get_line_list()
    response_tfl = get_all_routes(lines)
    return extract_routes(response_tfl)
    # routes[line] = list_routes(r_inbound)

