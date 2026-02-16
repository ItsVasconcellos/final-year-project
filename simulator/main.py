import network
from pyarrow import TimestampScalar
import pyarrow.parquet as pq
import pyarrow.compute as pc
from datetime import datetime,timedelta
import bisect 
import os
import sys
from mockdata import trips

trip_parquet_file_path = ".output/timetable/trips.parquet"
time_list_file_path = ".output/timetable/timelist.parquet"

total_network_delay = 0

def main(d_percentage, d_minutes):
    # atm no need for the railway network
    # railway_network = network.get_railway_graph()

    # Load the parquet file that contains all the trips
    # trips = pq.read_table(trip_parquet_file_path)
    # Read the parquet file which contains all the times in a unique column. That's why just using the first index.
    # time_list = pq.read_table(time_list_file_path)[0]
    # # convert from py_arrow timestamp to datetime
    # time_list = [x.as_py() for x in time_list]
    time_list = []
    for trip in trips.to_pylist():
        for o in range(0,len(trip["path"])):
            time_list.append(trip["arrival_times"][o])
    time_list.sort()
    # List of active_trips (live trips) and final trips (trips that have ended)
    active_trips:list[dict] = []
    final_trip_list:list[dict] = []
    print("Total number of trips: " + str(len(trips)))
    # Iterate through all the time_list available
    i = 0
    while i < len(time_list):
        # Verifying if any trip has started 
        new_trips = verify_new_trips(trips=trips,time=time_list[i])
        # Call function to add trips
        add_new_trips(new_trips=new_trips, active_trips=active_trips, time=time_list[i])
        print(time_list[i].strftime('%D-%H:%M'))
        # Looping through the active trips and moving to the next station if it arrived
        for trip in active_trips[:]:
            # can_go_to_next_station = has_every_train_arrived(active_trip=trip, active_trips=active_trips, time=time_list[i], time_list=time_list)
            # print(trip["path"])
            # # print([date_obj.strftime('%H-%M') for date_obj in trip["arrivals_time"]])
            # # print([date_obj.strftime('%H-%M') for date_obj in trip["departures_time"]])
            # print([date_obj.strftime('%H-%M') for date_obj in trip["expected_arrival_time"]])
            # print([date_obj.strftime('%H-%M') for date_obj in trip["expected_departure_time"]])                
            # print([date_obj.strftime('%H-%M') for date_obj in trip["actual_arrival_time"]])
            # print([date_obj.strftime('%H-%M') for date_obj in trip["actual_departure_time"]])
            # input()
            # If all previous trains to that station have arrived, the train will departure
            # if not can_go_to_next_station:
            #     continue
            move_to_next_station(trip=trip, time=time_list[i], time_list=time_list, d_min=d_minutes, d_percent=d_percentage)
            #Verify if trip has ended
            is_trip_over = is_last_station(active_trip=trip, time=time_list[i])
            # If the trips was on the last station and succesfully arrived at the last station, remove it from the active trips
            if is_trip_over:
                index = active_trips.index(trip)
                trip_ended = active_trips.pop(int(index))
                final_trip_list.append(trip_ended)
                continue
            has_every_train_arrived(active_trip=trip, active_trips=active_trips, time=time_list[i], time_list=time_list)
        i+=1

    # Debugging prints 
    print("Finished trips")
    print("Finished trips - " + str(len(final_trip_list)))
    print(time_list[i-1])
    
    # for i, trip in enumerate(final_trip_list):
    #     print(trip["path"])
    #     print(" - size: " + str(len(trip["path"])))
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["arrival_times"]])
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["actual_arrival_time"]])
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["expected_departure_time"]])
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["actual_departure_time"]])
    # print("Active trips")
    # for j,trip in enumerate(active_trips):
    #     if j > 50: break
    #     print(trip["path"])
    #     print(" - size: " + str(len(trip["path"])))
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["arrival_times"]])
    #     print([date_obj.strftime('%H-%M') for date_obj in trip["actual_arrival_time"]])
    #     if active_trips:
    #         input()
    #         print(time_list[i])


    print(len(final_trip_list))
    print("Number of remaining: " + str(len(active_trips)))
    print("Total delay in network (M) - " + str(total_network_delay))
    # save_trips(final_trip_list)
    
def verify_new_trips(trips,time):
    # Create a filter verifying if the first_departure matches with the time active and return the trips found in parquet file
    mask = pc.equal(trips["first_departure"],time)
    return trips.filter(mask).to_pylist()

def add_new_trips(new_trips, active_trips, time):
    for trip in new_trips:
        trip["next_station_index"] = 1
        trip["expected_arrival_time"] = trip["arrival_times"].copy()
        trip["expected_departure_time"] = trip["departure_times"].copy()
        trip["actual_arrival_time"] = [time]
        trip["actual_departure_time"] = []
        has_every_train_arrived(active_trip=trip,time=time,active_trips=active_trips,time_list=[])
        active_trips.append(trip)

def is_last_station(active_trip,time):
    """
    returns true if this is the last station the train is supposed to be    
    :param active_trip: a valid dict trip containing the full path and station index 
    """
    if len(active_trip["path"])-1 < active_trip["next_station_index"]:
        active_trip["actual_departure_time"].append(time)    
        return True
    return False

# Define parameters for percenatge of trip that has delay and the length of delay
# Counter for total delay on network - DONE
# Shifting focus to the london subway network - Are we sure? 
def move_to_next_station(trip, time, time_list,d_min, d_percent):
    """
    Docstring for move_to_next_station
    
    :param trip: Description
    :param time: Description
    :param time_list: Description
    :param d_min: Description
    :param d_percent: Description
    """
    next_station = trip["next_station_index"]
    time_to_arrive_next_station = trip["expected_arrival_time"][next_station]
    # Check if train is supposed to arrive at the station, if not return false
    if time < time_to_arrive_next_station:
        return False
    # Create a small amount of trips with delay. This distribution is more likely prone to numbers that will be round to 0, therefore no delay.
    # if trip["arrival_times"][next_station] + timedelta(minutes=10) > trip["expected_arrival_time"][next_station]:   
        # has_delay = round(random.randrange(1,10))
        # if has_delay == 9:
        #     print("Test")
    if trip["path"][next_station] == "TRI" and trip["arrival_times"][next_station] + timedelta(minutes=10) > trip["expected_arrival_time"][next_station]: 
        global total_network_delay
        total_network_delay += d_min
        for i in range(next_station,len(trip["path"])):
            new_time_expected =  trip["expected_arrival_time"][i] + timedelta(minutes=d_min)
            trip["expected_arrival_time"][i] = new_time_expected
            trip["expected_departure_time"][i] = new_time_expected
            if new_time_expected not in time_list:
                bisect.insort(time_list, new_time_expected)
                print(new_time_expected.strftime("%H:%M"))
                print("Oi")
        return False 
    trip["actual_arrival_time"].append(time)
    trip["next_station_index"] += 1
    return True

def has_every_train_arrived(active_trip, time, active_trips, time_list):
    # Get the station it is located atm
    next_station  = active_trip["next_station_index"]
    actual_station = next_station-1
    station_name = active_trip["path"][actual_station] 
    trip_arrival_time = active_trip["actual_arrival_time"][-1]
    if active_trip["arrival_times"][actual_station] == trip_arrival_time:
        for trip in active_trips:
            if station_name not in trip["path"]:
                continue
            station_index = trip["path"].index(station_name)
            expected_arrival_time = trip["arrival_times"][station_index]
            # if time > expected_arrival_time:
            #     continue
            trip_has_not_arrived = len(trip["actual_arrival_time"]) < station_index
            if trip_arrival_time >= expected_arrival_time and trip_has_not_arrived:
                # print(active_trip["path"])
                # print(actual_station)
                # print(station_name)
                return False
    if len(active_trip["actual_arrival_time"]) == next_station and len(active_trip["actual_arrival_time"]) != len(active_trip["actual_departure_time"]):
        print("Len Arrival:" + str(len(active_trip["actual_arrival_time"])) + " Next:" + str(next_station))
        active_trip["actual_departure_time"].append(time)
    return True

def save_simulation():
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("delay_percentage", help="Percentage of trips that will have delay", type=int)
    parser.add_argument("delay_minutes", help="How many minutes a single delayed trip should be delayed", type=int)
    args = parser.parse_args()
    if args.delay_percentage < 0 or args.delay_percentage > 100:
        raise argparse.ArgumentError("The percentage must be a valid integer number between 0 and 100")
    if args.delay_minutes <=0:
        raise argparse.ArgumentError("The trip cannot be delayed by negative minutes.")

    main(args.delay_percentage, args.delay_minutes)