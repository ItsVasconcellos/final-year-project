import networkx as nx
import csv

stations_name_dict = {}
unique_routes = {}

def get_stations():
    with open(file="../database/stations.csv", mode='r') as stationsFile:
        stations = csv.DictReader(stationsFile)
        for station in stations: 
            stations_name_dict[station["code"]] = station["name"]

def get_routes():
    with open(file="../database/routes.tsv", mode='r') as routesFile:
        count = 0
        routes = csv.reader(routesFile, delimiter="\t")
        for route in routes:
            if unique_routes.get(''.join(route)):
                unique_routes[''.join(route)] += 1
                continue
            unique_routes[''.join(route)] = 1
            count+=1
            print(route)
        print(count)

def avg_value():
    sum = 0
    for route in unique_routes.items():
        sum = sum + route[1]
    avg = sum/len(unique_routes)
    print(avg)

def max_value():
    station = ""
    maximum = 0
    for route in unique_routes.items():    
        if route[1] >= int(maximum):
            station = route[0]
            maximum = route[1]
    print(station)
    print(maximum)

# avg_value()
# max_value()

def main():
    get_stations()
    get_routes()
