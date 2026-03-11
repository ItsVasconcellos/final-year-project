import requests
import lines as l
import routes
import logging as log
import copy
from datetime import datetime, timedelta

def get_timetable_for_route(line, route):
    origin = route[0]
    dest = route[1]
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/Timetable/" + origin +  "/to/" + dest)
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

def extract_times(req):
    if req == None:
        return []
    if not req.get("stops"):
        log.warning("Stops not found: " + str(line))
        return {}
    if not req.get("timetable"):
        log.warning("timetable not found: " + str(line))
        return []
    line = req["lineId"]
    req_timetable = req["timetable"]
    interval_between_stations = []
    start_times = []
    final_trips = []
    for r in req_timetable["routes"]:
        stationIntervals = ["stationIntervals"][0]
        intervals = stationIntervals["intervals"]
        interval_between_stations = [x for x in intervals["timeToArrival"]]    
        for s in req_timetable["scheduele"]:
            if s["name"] != "Monday - Friday":
                continue
            for j in s["knownJourneys"]: 
                if j["intervalId"] != 0:
                    continue
                hour = str(j["hour"])
                min = str(j["min"])
                fmt = "%H:%M"
                start_dt = datetime.strptime(hour+":"+min, fmt)
                start_times.append(datetime(start_dt))
    for time in start_times:
        trip = [time]
        new_time = time
        for interval in interval_between_stations:
            new_time = time_addition(new_time,interval)
            trip.append(new_time)
        final_trips.append(trip)
    return final_trips

if __name__ == "__main__":
    list_routes = routes.main()
    final_timetable = []
    count = 0
    for name, route in list_routes.items():
        count +=1
        for r in route:
            count +=1
            raw_timetable = get_timetable_for_route(name, r)
            clean_timetable = {}
            arrival_time = extract_times(raw_timetable)
            if len(arrival_time) == 0:
                continue
            departure_time = copy.deepcopy(arrival_time)
            clean_timetable["path"], clean_timetable["stations"] = extract_path(raw_timetable)
            createTimeTable(clean_timetable,arrival_time, departure_time)
            final_timetable.append(clean_timetable)
    print(final_timetable)
    print(count)
    # save in parquet
    
