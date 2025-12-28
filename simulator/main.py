import csv
import network

def get_routes() -> dict:
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

def main():
    railway_network = network.create_graph()
    print(railway_network)

if __name__ == "__main__":
    main()