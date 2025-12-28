import networkx as nx
import csv

stations_name_dict = {}

def get_stations():
    with open(file="../database/stations.csv", mode='r') as stationsFile:
        stations = csv.DictReader(stationsFile)
        for station in stations: 
            stations_name_dict[station["code"]] = station["name"]

def get_routes():
    with open(file="../database/routes.tsv", mode='r') as routesFile:
        routes = csv.reader(routesFile, delimiter="\t")
        for route in routes: 
            print(route)



# get_stations()
get_routes()
