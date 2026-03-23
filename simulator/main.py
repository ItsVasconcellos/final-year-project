import network
from pyarrow import TimestampScalar
import pyarrow.parquet as pq
import pyarrow.compute as pc
from datetime import datetime,timedelta
import bisect 
import os
import random
from collections import defaultdict

trip_parquet_file_path = ".output/timetable2/trips.parquet"
time_list_file_path = ".output/timetable2/timelist.parquet"

total_delay_generated = 0
total_delay_propagated_in_network = 0

# Update the scenario of delay
# One minute after another
# Changing to just subway lines
# Number of trips that were affected
# Average delay on stations or trips
# 

def main(d_percentage, d_minutes, type_data):
    """
    Docstring for main
    
    :param d_percentage: the delay percentage that will be used 
    :param d_minutes: Description
    :param type_data: Defines if the simulation will use a small set of data (mock) or the actual timetable (real).
    """
    trips, time_list = get_data(type_data)
    # Process trips to have a station map
    active_station_map = defaultdict(set)
    # Define which stations will be delayed
    delay_list = random_delay_stations(trips, percent=d_percentage)

    # List of active_trips (live trips) and final trips (trips that have ended)
    active_trips:dict[dict] = {}
    final_trip_list:list[dict] = []
    print("Total number of trips: " + str(len(trips)))
    
    # Iterate through all the time_list available
    i = 0
    while i < len(time_list):
        time_now = time_list[i]
        # Verifying if any trip has started 
        new_trips = verify_new_trips(trips=trips,time=time_now)
        # Call function to add trips
        add_new_trips(new_trips=new_trips, active_trips=active_trips, time=time_now, time_list=time_list, delay_list=delay_list, d_min=d_minutes)
        add_trip_to_map_station(new_trips=new_trips, station_map=active_station_map)

        #Trips that has ended
        ended_trips_ids = [] 

        # Looping through the active trips and moving to the next station if it arrived
        for trip in active_trips.values():
            # can_go_to_next_station = has_every_train_arrived(active_trip=trip, active_trips=active_trips, time=time_list[i], time_list=time_list)
            move_to_next_station(trip=trip, time=time_now)
            #Verify if trip has ended
            is_trip_over = is_last_station(active_trip=trip, time=time_now)
            # If the trips was on the last station and succesfully arrived at the last station, remove it from the active trips
            if is_trip_over:
                ended_trips_ids.append((trip["id"]))
                final_trip_list.append(active_trips[trip["id"]])
                remove_trip_from_active_map(trip=trip, station_map=active_station_map)
                continue
            # If all previous trains to that station have arrived, the train will departure
            can_depart = check_departure(active_trip=trip)
            if can_depart:
                every_train_has_arrived = check_for_connections(active_trip=trip, active_trips=active_trips, active_stations_map=active_station_map)
                if every_train_has_arrived:
                    depart_trip(active_trip=trip,time=time_now, time_list=time_list)
                    check_delay(trip=trip,delay_list=delay_list, time_list=time_list, d_min=d_minutes)
        # print(i)
        # print(time_list[i])
        for ended_t in ended_trips_ids:
            active_trips.pop(ended_t)
        i+=1

    # Debugging prints 
    # print("Finished trips - " + str(len(final_trip_list)))

    print("Time simulation ended at " + time_list[i-1].strftime("%d/%m/%y - %H:%M"))
    print("Total trips simulates that have ended:" + str(len(final_trip_list)))
    print("Number of remaining: " + str(len(active_trips)))
    print("Total delay generated artificially in network (M) - " + str(total_delay_generated))
    print("Total delay propagated in network (M) - " + str(total_delay_propagated_in_network))
    # print("Total trips delayed in the network" + str(total_delay_propagated_in_network))

def get_data(type_data):
    if type_data == "real":
        # Load trips and time_list (just first index because its a one-column file) from parquet files and convert from py_arrow to a python list
        trips = pq.read_table(trip_parquet_file_path)
        time_list = pq.read_table(time_list_file_path)[0]
        time_list = [x.as_py() for x in time_list]
        return trips, time_list    
    # Alternative to get the time_list if using mock data
    
    from mockdata import trips
    time_list = []
    for trip in trips.to_pylist():  
        for o in range(0,len(trip["path"])):
            if trip["arrival_times"][o] not in time_list:
                time_list.append(trip["arrival_times"][o])
    time_list.sort()
    # trips["has_delay"] = False
    return trips, time_list

def add_trip_to_map_station(new_trips, station_map):
    for t in new_trips:
        for s in t["path"]:
            station_map[s].add(t["id"])

def remove_trip_from_active_map(trip,station_map):
    for s in trip["path"]:
        station_map[s].discard(trip["id"])

def random_delay_stations(trips,percent):
    total_trips = pc.sum(pc.list_value_length(trips["path"])).as_py()
    total_stations_with_delay = round((total_trips*percent)/100)
    if total_stations_with_delay == 0:
        return {}
    
    delayed_stations = sorted(random.sample(range(total_trips), total_stations_with_delay))
    final_delayed_station = defaultdict(list)
    # indexes
    start_path = 0
    end_path = 0
    i = 0
    value = delayed_stations[i]
    for trip in trips.to_pylist():
        trip_id = trip["id"]
        end_path += len(trip["path"])
        while len(delayed_stations) > i:
            value = delayed_stations[i]
            if end_path <= value:
                break
            if value >= start_path:
                index = value - start_path 
                final_delayed_station[trip_id].append(index)
            i +=1
        start_path = end_path 
    return final_delayed_station

def verify_new_trips(trips,time):
    # Create a filter verifying if the first_departure matches with the time active and return the trips found in parquet file
    mask = pc.equal(trips["first_departure"],time)
    return trips.filter(mask).to_pylist()

def add_new_trips(new_trips, active_trips, time, time_list, delay_list, d_min):
    for trip in new_trips:
        trip["next_station_index"] = 1
        trip["expected_arrival_time"] = trip["arrival_times"].copy()
        trip["expected_departure_time"] = trip["departure_times"].copy()
        trip["actual_arrival_time"] = [time]
        trip["actual_departure_time"] = []
        trip["station_to_idx"] = {name: i for i, name in enumerate(trip["path"])}
        if 0 in delay_list[trip["id"]]: 
            global total_delay_generated, total_delay_propagated_in_network
            delay = random.randrange(0,d_min)
            total_delay_generated += delay
            total_delay_propagated_in_network += delay
            for i in range(0,len(trip["path"])):
                new_time_expected =  trip["expected_arrival_time"][i] + timedelta(minutes=delay)
                trip["expected_arrival_time"][i] = new_time_expected
                trip["expected_departure_time"][i] = new_time_expected
                trip["has_delay"] = True
                if new_time_expected not in time_list:
                    bisect.insort(time_list, new_time_expected)
        active_trips[trip["id"]] = trip

def is_last_station(active_trip,time):
    """
    returns true if this is the last station the train is supposed to be    
    :param active_trip: a valid dict trip containing the full path and station index 
    """
    if len(active_trip["path"])-1 < active_trip["next_station_index"]:
        active_trip["actual_departure_time"].append(time)    
        return True
    return False

# Define parameters for percenatge of trip that has delay and the length of delay - Half done
# Counter for total delay on network - DONE
# Shifting focus to the london subway network - Are we sure? 
def move_to_next_station(trip, time):
    """
    This function is responsible for checking if the train arrived in the next station and also generate some delay into the network    
    :param trip: Description
    :param time: Description
    """
    next_station = trip["next_station_index"]
    time_to_arrive_next_station = trip["expected_arrival_time"][next_station]
    # Check if train is supposed to arrive at the station, if not return false
    arrivals = len(trip["actual_arrival_time"])
    departures = len(trip["actual_departure_time"])
    if time < time_to_arrive_next_station or arrivals != departures:
        return False
    # Create a small amount of trips with delay. This distribution is more likely prone to numbers that will be round to 0, therefore no delay.
    trip["actual_arrival_time"].append(time)
    trip["next_station_index"] += 1
    return True

def check_for_connections(active_trip, active_trips, active_stations_map):
    """
    Returns false if there is a pending trip for the current station
    Return true if all trips have arrived
    """
    # Get the next station the trip will head to
    next_station  = active_trip["next_station_index"]
    # Get current station the train is in
    actual_station = next_station-1
    # Name of the current station
    station_name = active_trip["path"][actual_station] 
    # Original time of arrival
    arrival_time = active_trip["arrival_times"][actual_station]
    # Verify if there are any trip, amongst the trips that are active, that a connection could be made originally
    list_trips_for_station = active_stations_map[station_name]
    for trip in list_trips_for_station:
        # Don't compare to itself
        if trip == active_trip["id"]:
            continue
        # If the station is not on the trip, we should not bother
        t = active_trips[trip]
        # Index 
        station_index = t["station_to_idx"][station_name]

        original_trip2_arrival_time = t["arrival_times"][station_index]
        # If the arrival time of the active_trip was previous to the expected time of the trip being compared, it means nobody could get a connection from a to b. Therefore, not a valid case. 
        if arrival_time <= original_trip2_arrival_time:
            continue
        trip_has_arrived = t["next_station_index"] > station_index
        if not trip_has_arrived:
            # print("Trip yet to arrive:" + str(trip["id"]) + " - trip that will be delayed: " + str(active_trip["id"]) + " - Time as of now: " + time.strftime("%H:%M") + " - tA: " + arrival_time.strftime("%H:%M") + " - expectedA: " + original_trip2_arrival_time.strftime("%H:%M") )
            return False
    return True

def check_departure(active_trip):
    next_station  = active_trip["next_station_index"]
    ### Verify if trip has already arrived at the station being verified and if it has not departed yet. If both of these are true, trip will departure
    if len(active_trip["actual_arrival_time"]) == next_station and len(active_trip["actual_arrival_time"]) != len(active_trip["actual_departure_time"]):
        return True
    return False

def depart_trip(active_trip, time, time_list):
    next_station  = active_trip["next_station_index"]
    actual_station = next_station - 1
    active_trip["actual_departure_time"].append(time)
    # In case the trip departured later than expected, the expected times will be adjusted to match this.
    if time != active_trip["expected_departure_time"][actual_station]:
        adjust_expected_time(active_trip, time, next_station, time_list)

def check_delay(trip, delay_list, time_list, d_min):
    next_station = trip["next_station_index"]
    if next_station in delay_list[trip["id"]]: 
        global total_delay_generated, total_delay_propagated_in_network
        delay = random.randrange(0,d_min)
        total_delay_generated += delay
        total_delay_propagated_in_network += delay
        for i in range(next_station,len(trip["path"])):
            new_time_expected = trip["expected_arrival_time"][i] + timedelta(minutes=delay)
            trip["expected_arrival_time"][i] = new_time_expected
            trip["expected_departure_time"][i] = new_time_expected
            trip["has_delay"] = True
            if new_time_expected not in time_list:
                bisect.insort(time_list, new_time_expected)

def adjust_expected_time(active_trip, time, next_station, time_list):
    """
    This function adjust times for delays due to departuring later than expected.
    It will calculate how long the distance between two stations would normally take and adjust the sum to the value of departure (or expected departure in the case of future stations)
    """
    delta = time
    diff_in_departures = int((time - active_trip["expected_departure_time"][next_station-1]).total_seconds() // 60) 
    global total_delay_propagated_in_network
    total_delay_propagated_in_network += diff_in_departures
    for i in range(next_station,len(active_trip["path"])):
            delta += active_trip["arrival_times"][i] - active_trip["arrival_times"][i-1] 
            new_time_expected = delta
            active_trip["expected_arrival_time"][i] = new_time_expected
            active_trip["expected_departure_time"][i] = new_time_expected
            if new_time_expected not in time_list:
                bisect.insort(time_list, new_time_expected)

def save_simulation():
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("delay_percentage", help="Percentage of trips that will have delay", type=float)
    parser.add_argument("delay_minutes", help="How many minutes a single delayed trip should be delayed", type=int)
    parser.add_argument("type_data", help="If you want to use real data or mocked data (simplified)", type=str, choices=["real","mock"])
    args = parser.parse_args()
    if args.delay_percentage < 0 or args.delay_percentage > 100:
        raise argparse.ArgumentError("The percentage must be a valid integer number between 0 and 100")
    if args.delay_minutes <=0:
        raise argparse.ArgumentError("The trip cannot be delayed by negative minutes.")

    main(args.delay_percentage, args.delay_minutes, args.type_data)