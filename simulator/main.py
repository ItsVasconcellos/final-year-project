import network
from pyarrow import TimestampScalar
import pyarrow.parquet as pq
import pyarrow.compute as pc
from datetime import datetime
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
    final_trip:list[dict] = []

    # Iterate through all the time_list available
    i = 0
    while i < len(time_list):
        # if i > 50: 
        #     break
        # print("\n")
        # print(time)
        # print(active_trips)
        
        # Looping through the active trips and moving to the next station if it arrived
        for trip in active_trips[:]:

            if is_trip_over(active_trip=trip, active_trips=active_trips, final_trip=final_trip):
                continue
            
            move_to_next_station(trip=trip, time=time_list[i])

        # Verifying if any trip has started and add to active trips
        new_trips = verify_new_trips(trips,time_list[i])
        if len(new_trips) >= 1: add_new_trips(new_trips=new_trips, active_trips=active_trips)
        
        i+=1

    for i, trip in enumerate(final_trip):
        print(trip)
        # print(len(trip["path"]))
        # print(trip["station"])
    print(len(final_trip))

def verify_new_trips(trips,time):
    # Create a filter verifying if the first_departure matches with the time active and return the trips found in parquet file
    mask = pc.equal(trips["first_departure"],time)
    return trips.filter(mask).to_pylist()

def add_new_trips(new_trips, active_trips):
    for trip in new_trips:
        trip["next_station_index"] = 1
        active_trips.append(trip)

def is_trip_over(active_trip, final_trip, active_trips):
    # If trip ended, remove from active trips and add to the final_trip list
    if len(active_trip["path"]) - 1 == active_trip["next_station_index"]:
        index = active_trips.index(active_trip)
        trip_ended = active_trips.pop(int(index))
        final_trip.append(trip_ended)
        return True
    
    # If not, return False
    return False

def move_to_next_station(trip, time):
    next_station = trip["next_station_index"]   
    if time == trip["arrival_times"][next_station]:
        # trip["actual_arrival_time"]
        trip["next_station_index"] += 1

if __name__ == "__main__":
    main()