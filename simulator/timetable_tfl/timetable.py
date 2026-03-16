import bisect 
import requests
import lines as l
import routes as RouteService
import logging as log
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.parquet as pq
import os
import time

def get_timetable_for_route(line, route):
    origin = route[0]
    dest = route[1]
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/Timetable/" + origin +  "/to/" + dest)
    time.sleep(1)
    return inbound.json()

def get_line_list():
    lines = l.get_lines()
    lines_id = ""
    for line in lines:
        lines_id += line["name"] + ","
    return lines_id[:-1]

def extract_path(req):
    # Check if there is any information or is null
    if req == None:
        return []
    if not req.get("stops"):
        return {}

    line = req["lineId"]
    path = []
    stations = []
    for s in req["stops"]:
        if not s.get("stationId"):
            log.warning("station not found: " + str(line))
            continue
        path.append(s["stationId"])
        stations.append(s["name"])
    return path,stations

def time_addition(start, quantity):
    return (start + timedelta(minutes=quantity))

def extract_stations_and_intervals(req_timetable):
    if req_timetable == None:
        log.warning("Timetable not found")
        return []
    # if not req.get("timetable"):
    #     log.warning("timetable not found: " + str(line))
    #     return []
    ## Get the important part, since the key timetable-routes contains both the interval between stations and times that each route start
    departure_stop = req_timetable["departureStopId"]
    req_routes = req_timetable["routes"]
    routes = {}
    stationIntervals = req_routes[0]["stationIntervals"]
    for station in stationIntervals:
        id = station["id"]
        routes[id] = {}
        stations = [departure_stop]
        interval_between_stations = []
        intervals = station["intervals"]
        for i in intervals:
            interval_between_stations.append(i["timeToArrival"])
            stations.append(i["stopId"])
        routes[id]["stations"] = stations
        routes[id]["time_diff"] = interval_between_stations
    return routes

def extract_start_times(time_list, req_timetable):
    req_routes = req_timetable["routes"]
    schedules = req_routes[0]["schedules"]
    journey_list = []
    for s in schedules:
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if s["name"] != "Monday - Friday":
            continue
        journey_dict ={}
        for j in s["knownJourneys"]: 
            date_now = base_date + timedelta(hours=int(j["hour"]), minutes=int(j["minute"]))
            journey_dict["start"] = date_now
            journey_dict["route"] = str(j["intervalId"])
            if date_now not in time_list:
                bisect.insort(time_list, journey_dict["start"])
            journey_list.append(journey_dict)
    return journey_list

def create_trip_times(journey_list,routes, time_list):
    final_trips = []
    for journey in journey_list:
        id_route = journey["route"]
        log.info("Route id: " + str(id_route))
        route = routes[id_route]
        new_time = journey["start"]
        
        trip={}
        trip["path"] = route["stations"]
        trip["arrival_time"] = [new_time]
        trip["first_departure"] = new_time
        
        for interval in route["time_diff"]:
            new_time = time_addition(new_time,interval)
            if new_time not in time_list:
                    bisect.insort(time_list, new_time)
            trip["arrival_time"].append(new_time)
        final_trips.append(trip)
    return final_trips

    
## Get all the availables routes, including stations id and time
## See all the time routes occours and match with their route id
## Create all the trips for 


def create_time_table(trip_list, final_timetable,trip):
    for item in trip_list:
        timetable = {}
        timetable["id"] = trip
        timetable["path"] = item["path"]
        timetable["arrival_times"] = item["arrival_time"]
        timetable["departure_times"] = item["arrival_time"]
        timetable["first_departure"] = item["first_departure"]
        final_timetable.append(timetable)
        trip +=1
    return trip

def save_timetable(timetable,list_of_times):
    schema = pa.schema([
        ('id',pa.int64()),
        ('path', pa.list_(pa.string())),          
        ('arrival_times', pa.list_(pa.timestamp("s"))), 
        ('departure_times', pa.list_(pa.timestamp("s"))),
        ('first_departure', pa.timestamp("s"))          
    ])
    trip_table = pa.Table.from_pylist(timetable,schema)
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")
    if not os.path.exists(os.path.join(os.getcwd(), '.output/timetable2')):
        os.mkdir(".output/timetable2", mode=0o777, dir_fd=None)
    pq.write_table(trip_table,".output/timetable2/trips.parquet")
    time_schema = pa.schema([
        ('time', pa.timestamp('s'))
    ])
    # Save the list of times in a json file for later acceess in simulation
    time_table = pa.Table.from_arrays([list_of_times], schema=time_schema)
    pq.write_table(time_table, ".output/timetable2/timelist.parquet")

if __name__ == "__main__":
    list_routes = RouteService.main()
    final_timetable = []
    time_list = []
    trip_id = 0
    count_routes= 0
    count_journey = 0
    for name, route in list_routes.items():
        for r in route:
            raw_timetable = get_timetable_for_route(name, r)
            if not raw_timetable.get("timetable"):
                log.warning("timetable not found: ")
                print(raw_timetable)
                print("\n")
                continue
            req_timetable = raw_timetable.get("timetable")
            path_with_intervals = extract_stations_and_intervals(req_timetable=req_timetable)
            if len(path_with_intervals) == 0:
                continue
            count_routes+= len(path_with_intervals)
            journey_list = extract_start_times(time_list=time_list,req_timetable= req_timetable)
            count_journey += len(journey_list)
            trips = create_trip_times(journey_list=journey_list, routes=path_with_intervals, time_list=time_list)
            # create_trips = extract_path(raw_timetable)
            trip_id = create_time_table(trips,final_timetable, trip_id)
    save_timetable(final_timetable,list_of_times=time_list)
    # print(final_timetable)
    print(trip_id)
    print(count_routes) 
    print(count_journey)
    # save in parquet
    
