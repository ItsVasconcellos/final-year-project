import network
from pyarrow import TimestampScalar
import pyarrow.parquet as pq
import pyarrow.compute as pc
from datetime import datetime,timedelta
import random
import bisect 
import os
import sys

trip_parquet_file_path = ".output/timetable/trips.parquet"
time_list_file_path = ".output/timetable/timelist.parquet"

def main():
    # atm no need for the railway network
    # railway_network = network.get_railway_graph()
    
    # Load the parquet file that contains all the trips
    trips = pq.read_table(trip_parquet_file_path)
    # Read the parquet file which contains all the times in a unique column. That's why just using the first index.
    time_list = pq.read_table(time_list_file_path)[0]
    # convert from py_arrow timestamp to datetime
    time_list = [x.as_py() for x in time_list]
    # List of active_trips (live trips) and final trips (trips that have ended)
    active_trips:list[dict] = []
    final_trip_list:list[dict] = []

    # Iterate through all the time_list available
    i = 0
    while i < len(time_list):
        # if i > 200:
        #     break
        
        # Looping through the active trips and moving to the next station if it arrived
        for trip in active_trips[:]:
            #Verify if trip has ended
            is_trip_over = is_last_station(active_trip=trip)
            arrived_at_next_station = move_to_next_station(trip=trip, time=time_list[i], time_list=time_list, active_trips=active_trips)
            # If the trips was on the last station and succesfully arrived at the last station, remove it from the active trips
            if is_trip_over and arrived_at_next_station:
                index = active_trips.index(trip)
                trip_ended = active_trips.pop(int(index))
                final_trip_list.append(trip_ended)
                continue
            
        # Verifying if any trip has started 
        new_trips = verify_new_trips(trips=trips,time=time_list[i])
        # Call function to add trips
        add_new_trips(new_trips=new_trips, active_trips=active_trips, time=time_list[i])
        
        i+=1
    # Debugging prints 
    for i, trip in enumerate(final_trip_list):
        print(trip["path"])
        print([date_obj.strftime('%H-%M') for date_obj in trip["arrival_times"]])
        print([date_obj.strftime('%H-%M') for date_obj in trip["expected_arrival_time"]])
    print(len(time_list))
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
        trip["actual_departure_time"] = [time]
        active_trips.append(trip)

def is_last_station(active_trip):
    """
    returns true if this is the last station the train is supposed to be    
    :param active_trip: a valid dict trip containing the full path and station index 
    """
    if len(active_trip["path"])-1 > active_trip["next_station_index"]:
            return True
    return False

def move_to_next_station(trip, time, time_list, active_trips):
    next_station = trip["next_station_index"]
    name_next_station = trip["path"][next_station] 
    time_to_arrive_next_station = trip["expected_arrival_time"][next_station]
    # Check if train is supposed to arrive at the station, if not return false
    if time < time_to_arrive_next_station:
        return False
    # Create a small amount of trips with delay. This distribution is more likely prone to numbers that will be round to 0, therefore no delay.
    has_delay = round(random.betavariate(2,5))
    if has_delay == 1:
        delay_quantity_in_minutes = random.randrange(0,10)
        for i in range(next_station,len(trip["path"])):
            new_time_expected =  trip["expected_arrival_time"][i] + timedelta(minutes=delay_quantity_in_minutes)
            trip["expected_arrival_time"][i] = new_time_expected
            trip["expected_departure_time"][i] = new_time_expected
            if new_time_expected not in time_list:
                bisect.insort(time_list, new_time_expected)
        return False
    trip["next_station_index"] += 1
    trip["actual_departure_time"].append(time)
    trip["actual_arrival_time"].append(time)
    return True

def save_simulation():
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")

if __name__ == "__main__":
    main()