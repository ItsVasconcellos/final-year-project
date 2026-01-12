import network
import timetable as tt

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
    timetable = tt.main()



if __name__ == "__main__":
    main()