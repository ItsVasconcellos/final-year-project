import bisect 
import requests
import lines as l
import routes
import logging as log
import copy
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.parquet as pq
import os
import time

def get_timetable_for_route(line, route):
    origin = route[0]
    dest = route[1]
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/Timetable/" + origin +  "/to/" + dest)
    time.sleep(0.5)
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

def extract_times(time_list, req):
    if req == None:
        return []
    if not req.get("lineId"):
        log.warning("Line/Timetable not found")
        return []
    line = req["lineId"]
    if not req.get("stops"):
        log.warning("Stops not found: " + str(line))
        return {}
    if not req.get("timetable"):
        log.warning("timetable not found: " + str(line))
        return []
    req_timetable = req["timetable"]
    interval_between_stations = []
    start_times = []
    final_trips = []
    for r in req_timetable["routes"]:
        stationIntervals = r["stationIntervals"][0]
        intervals = stationIntervals["intervals"]
        for i in intervals:
            interval_between_stations.append(i["timeToArrival"])    
        for s in r["schedules"]:
            base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if s["name"] != "Monday - Friday":
                continue
            for j in s["knownJourneys"]: 
                if j["intervalId"] != 0:
                    continue
                hour = str(j["hour"])
                min = str(j["minute"])
                if len(min) == 1:
                    min = "0"+min
                start_dt = base_date + timedelta(hours=int(j["hour"]), minutes=int(j["minute"]))
                if start_dt not in time_list:
                    bisect.insort(time_list, start_dt)
                start_times.append(start_dt)
    for time in start_times:
        t_trip = [time]
        new_time = time
        for interval in interval_between_stations:
            new_time = time_addition(new_time,interval)
            if new_time not in time_list:
                    bisect.insort(time_list, new_time)
            t_trip.append(new_time)
        final_trips.append(t_trip)
    return final_trips

def create_time_table(path, station,arrival_time, departure_time, final_timetable,trip):
    for i in range(0,len(arrival_time)):
        timetable = {}
        timetable["id"] = trip
        timetable["path"] = path
        timetable["station"] = station
        timetable["arrival_times"] = arrival_time[i]
        timetable["departure_times"] = departure_time[i]
        timetable["first_departure"] = arrival_time[i][0]
        final_timetable.append(timetable)
        trip +=1
    return trip

def save_timetable(timetable,list_of_times):
    schema = pa.schema([
        ('id',pa.int64()),
        ('path', pa.list_(pa.string())),          
        ('station', pa.list_(pa.string())),          
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
    list_routes = routes.main()
    final_timetable = []
    time_list = []
    trip = 0
    for name, route in list_routes.items():
        for r in route:
            raw_timetable = get_timetable_for_route(name, r)
            arrival_time = extract_times(time_list,raw_timetable)
            if len(arrival_time) == 0:
                continue
            departure_time = copy.deepcopy(arrival_time)
            path,stations = extract_path(raw_timetable)
            trip = create_time_table(path, stations ,arrival_time, departure_time,final_timetable, trip)
    save_timetable(final_timetable,list_of_times=time_list)
    print(final_timetable)
    print(trip)
    # save in parquet
    
