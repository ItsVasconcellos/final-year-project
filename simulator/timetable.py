import openpyxl
import network
import routes
from datetime import datetime, timedelta

def main():
    # Read the excel files
    timetable = openpyxl.load_workbook("../database/timetable/CB02.xlsx")
    timetable_monday_fw = timetable["Mondays to Fridays Forward"]
    # Left out for the moment. First goal is to work with just one sheet of the excel file.
    timetable_monday_reverse = timetable["Mondays to Fridays Reverse"]
    
    routes_dict = {}
    routes_dict = extract_routes_and_times(timetable_file=timetable_monday_fw, routes_dict=routes_dict)
    routes_dict = extract_routes_and_times(timetable_file=timetable_monday_reverse, routes_dict=routes_dict)
    return create_timetable(routes_dict)

def extract_routes_and_times(timetable_file, routes_dict) -> dict:
    _,station_codes = network.get_stations()
    # keys_with_problem = []
    # list_station_code = []
    # Iterate through excel file and get the origin and destination, alongside time.
    for col in timetable_file.iter_cols(1, timetable_file.max_column):
        for row in range(2,4):
            if row == 2:
                origin = col[row].value
            elif row == 3:
                desintation = col[row].value

        if origin == None or desintation == None:
            continue

        if (len(origin.split("\n")) >= 2) and len(desintation.split("\n")) >= 2:
            origin_station = origin.split("\n")[0].title()
            desintation_station = desintation.split("\n")[0].title()
            time_departure = str(origin.split("\n")[1]).replace("½", "")
            time_arrival = str(desintation.split("\n")[1]).replace("½", "")
            origin_station_code = None
            desintation_station_code = None
            
            if station_codes.get(origin_station) and station_codes.get(desintation_station):
                origin_station_code = station_codes[origin_station]
                desintation_station_code = station_codes[desintation_station]
            
            ## This is temporary and just to verify the precision of the station code and if its failing or not. 
            # Since there are a lot of excel files and the names don't exactly match it will help sort bugs.
            # if station_codes.get(origin_station):
            #     station_code = station_codes[origin_station]
            #     origin_station_code = station_code
            #     if station_code not in list_station_code:
            #         list_station_code.append(station_code)
            # else:
            #     if origin_station not in keys_with_problem:
            #         keys_with_problem.append(origin_station)


            # if station_codes.get(desintation_station):
            #     station_code = station_codes[desintation_station]
            #     desintation_station_code = station_code
            #     if station_code not in list_station_code:
            #         list_station_code.append(station_code)
            # else:
            #     if desintation_station not in keys_with_problem:
            #         keys_with_problem.append(desintation_station)

            if origin_station_code != None and desintation_station_code != None:
                dict_key = origin_station_code + "_" + desintation_station_code
                dif = (time_diff(time_departure, time_arrival).seconds)/60
                if routes_dict.get(dict_key):
                    routes_dict[dict_key]["time"].append([time_departure,time_arrival]) 
                    if dif not in routes_dict[dict_key]["time_range"]:
                        routes_dict[dict_key]["time_range"].append(dif)
                    continue
                routes_dict[dict_key] = {"path": [origin_station_code,desintation_station_code], "time": [[time_departure, time_arrival]], "time_range": [dif] }

    # print(list_station_code)
    # print(keys_with_problem)
    return routes_dict

def time_diff(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)

    # if end time is earlier, it means next day
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    return end_dt - start_dt

def create_timetable(timetable_routes) -> list[dict]:
    all_routes = routes.get_all_routes_and_distances()
    timetable = []
    for timetable_item in timetable_routes.values():
        path = timetable_item["path"]
        time = timetable_item["time"]
        time_range:list =  timetable_item["time_range"]
        time_range.sort()
        time_range_quantity = len(time_range)
        # Verify if there is not a broken path
        if len(path) < 2 or len(time) < 1:
            continue
        
        distances_matched, matched_routes, number_of_routes_matched = match_routes(routes=all_routes, path=path)

        # If no matched route, just go for the next timetable
        if len(matched_routes) < 1:
            continue

        dict_meu = {}
        for t in time_range:
            if time_range_quantity > 1:
                index_distance = round(time_range.index(t) * (number_of_routes_matched-1)/(time_range_quantity-1))
            else: 
                index_distance = 0
            dict_meu[t] = index_distance

        for trip in time:
            start_time = trip[0]
            arrival_time = trip[1]
            diff = (time_diff(start_time,arrival_time).seconds)/60
            print(time_range)
            print(diff)
            index = dict_meu[diff]
            distance = distances_matched[index]
            print("Distancia: " + str(distances_matched))
            print(distance)
            route = matched_routes[distance]
            new_object = {
                "distance": distance,
                "path": route["path"],
                "arrival_time": [start_time,arrival_time],
                "departure_time":[start_time,arrival_time]
            }
            timetable.append(new_object)

    return timetable
    
def match_routes(routes: dict, path:dict)-> list[list,dict,int]:
    distances_matched = []
    matched_routes = {}
    for route in routes.values():
        # just verify if the route is existent and have a start and a end
        if len(route["path"]) <= 2:
            continue
        route_start = route["path"][0]
        route_end = route["path"][-1]
        if route_start == path[0] and route_end == path[1]:
            key = route["totalDistance"]
            matched_routes[key] = route
            distances_matched.append(key)
    distances_matched.sort()
    number_of_routes_matched = len(distances_matched)
    return distances_matched, matched_routes, number_of_routes_matched

if __name__ == "__main__":
    main()