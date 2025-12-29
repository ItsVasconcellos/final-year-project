import network
import routes

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

def create_time_table(routes):
    """
    Some assumptions were made here. 
    The sooner train will be at 5:00 and the latest will leave at 00:00
    For the final time, the calculus will be done through a constant of velocity. It will assume that Time*Velocity = Distance. 
    The distance is provided by the dataset and its the edges weight. The velocity is assumed to be a constant to simplify the equation.
    https://www.northernrailway.co.uk/travel/how-fast-do-northern-trains-go -> Average velocity is 65Mph/h which is equivalent to 104,6 km/h
    """
    pass



def main():
    railway_network = network.create_graph()
    print(railway_network)
    route = routes.process_routes_to_1_day()


if __name__ == "__main__":
    main()