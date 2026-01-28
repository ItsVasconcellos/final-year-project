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
        if i > 50: 
            break
        # print("\n")
        # print(time)
        # print(active_trips)
        
        # Looping through the active trips and moving to the next station if it arrived
        for active_trip in active_trips[:]:

            if len(active_trip["path"]) - 1 == active_trip["next_station_index"]:
                index = active_trips.index(active_trip)
                trip_ended = active_trips.pop(int(index))
                final_trip.append(trip_ended)
                continue
            
            next_station = active_trip["next_station_index"]
            if time_list[i] == active_trip["arrival_times"][next_station]:
                # active_trip["actual_arrival_time"]
                active_trip["next_station_index"] += 1
        
        # Verifying if any trip has started
        new_trips = verify_new_trips(trips,time_list[i])
        for trip in new_trips:
            trip["next_station_index"] = 1
            active_trips.append(trip)
        
        i+=1

    for i, trip in enumerate(final_trip):
        print(trip)
        # print(len(trip["path"]))
        # print(trip["station"])
    

def verify_new_trips(trips,time):
    mask = pc.equal(trips["first_departure"],time)
    return trips.filter(mask).to_pylist()
    

if __name__ == "__main__":
    main()