import openpyxl
import network
import routes

def main():
    # Read the excel files
    timetable = openpyxl.load_workbook("../database/timetable/CB02.xlsx")
    timetable_monday_fw = timetable["Mondays to Fridays Forward"]
    # Left out for the moment. First goal is to work with just one sheet of the excel file.
    # timetable_monday_reverse = timetable["Mondays to Fridays Reverse"]
    routes_dict = {}
    routes_dict = extract_routes_and_times(timetable_file=timetable_monday_fw, routes_dict=routes_dict)
   # Test
    # routes_dict = extract_routes_and_times(timetable_file=timetable_monday_reverse, routes_dict=routes_dict)
    # for i in routes_dict.values():
    #     print(i["path"])
    return match_routes(routes_dict)

def extract_routes_and_times(timetable_file, routes_dict) -> dict:
    _,station_codes = network.get_stations()
    keys_with_problem = []
    list_station_code = []
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
            time_departure = origin.split("\n")[1]
            time_arrival = desintation.split("\n")[1]
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
                if routes_dict.get(dict_key):
                    routes_dict[dict_key]["time"].append([time_departure,time_arrival])
                    continue
                routes_dict[dict_key] = {"path": [origin_station_code,desintation_station_code], "time": [[time_departure, time_arrival]] }

    # print(list_station_code)
    # print(keys_with_problem)
    return routes_dict

def match_routes(timetable_routes) -> list[dict]:
    all_routes = routes.get_all_routes()
    timetable = []
    for i, timetable_item in enumerate(timetable_routes.values()):
        matched_routes = []
        path = timetable_item["path"]
        time = timetable_item["time"]
        total_travels_timetable = len(time)
        path_total_travles = 0
        # Verify if there is not a broken path
        if len(path) < 2 or len(time) < 1:
            continue

        for route in all_routes.values():
            # just verify if the route is existent and have a start and a end
            if len(route["path"]) <= 2:
                continue
            route_start = route["path"][0]
            route_end = route["path"][-1]
            if route_start == path[0] and route_end == path[1]:
                matched_routes.append(route)
                path_total_travles += route["count"] 
        
        # If no matched route, just go for the next timetable
        if len(matched_routes) < 1:
            continue

        # Lixo 

        # What needs to happen next:
        # I need to find the actual amount of time that each path will recieve, so 
        values_to_distribute = total_travels_timetable - len(matched_routes)
        print(values_to_distribute)
        if values_to_distribute > 0:
            distribution_ratio = values_to_distribute/path_total_travles
            actual_total_travels  = 0
            for match in matched_routes:
                travel_amount =  int(match["count"] * distribution_ratio) + 1
                match["total_travel"] = travel_amount
                match["backup_total_travel"] = travel_amount
                actual_total_travels += travel_amount

            margin_error = total_travels_timetable - actual_total_travels
            if margin_error > 0: 
                for i in range(0, margin_error):
                    matched_routes[i]["total_travel"] += 1
                    # print("total travel: " + str(matched_routes[i]["total_travel"]))
                    matched_routes[i]["backup_total_travel"] += 1
            elif margin_error < 0: 
                for i in range(0, margin_error):
                    matched_routes[i]["total_travel"] -= 1

        else:
            for i, match in enumerate(matched_routes):
                if i < total_travels_timetable:
                    match["total_travel"] = 1 
                    match["backup_total_travel"] = 1 
            matched_routes = matched_routes[:total_travels_timetable]

        item = 0
        for i, t in enumerate(time):
            next_match = matched_routes[item]
            # print("\n")
            # print(next_match)
            if next_match["total_travel"] <= 0:
                found = False
                while not found:
                    item += 1
                    if item >= len(matched_routes): 
                        item = 0
                    next_match = matched_routes[item]
                    if next_match["total_travel"] > 0:
                        found = True
            if next_match.get("time"):
                next_match["time"].append(t)
                next_match["total_travel"] -= 1
            else:
                next_match["time"] = [t]
                next_match["total_travel"] -= 1
            if item + 1 >= len(matched_routes):
                item = 0
                continue
            item +=1
        
        timetable.extend(matched_routes)
    for item in timetable:
        print("\n Total travel time:" + str(item["backup_total_travel"]))
        print("Total len of time:" + str(len(item["time"])))
        # print(item["time"])
    return timetable
    
    # for route in timetable_routes.values():
    #     if len(route) >= 2:
    #         route_start = route[0]
    #         route_end = route[1]
    #         if route_start == "EUS" and route_end == "BHM":
    #             timetable_count += 1    
    #         count = 0
    #         routes_matched = []
    #         for r in all_routes.values():
    #             if len(r["path"]) >= 2 and r["path"][0] == route_start and r["path"][-1] == route_end:
    #                 # print(f"Match found: Timetable route {route} matches dataset route {r['path']}")
    #                 count += 1
    #                 routes_matched.append(r["count"])
    #         # if count > 2:
    #         #     print(routes_matched)
    #         #     print(f"Timetable route from {route_start} to {route_end} matches {count} dataset routes.")
    # print(f"Total timetable routes matching EUS to BHM: {timetable_count}")

def old_main():
    timetable = openpyxl.load_workbook("../database/timetable/CB02.xlsx")
    timetable_monday_fw = timetable["Mondays to Fridays Forward"]
    timetable_monday_reverse = timetable["Mondays to Fridays Reverse"]
    _,station_codes = network.get_stations()
    keys_with_problem = []
    list_station_code = []
    routes_list = {}
    # Origin loop
    for col in timetable_monday_fw.iter_cols(1, timetable_monday_fw.max_column):
        value = col[2].value
        column = col[2].column 
        if value == None:
            continue

        if len(value.split("\n")) >= 2:
            station = value.split("\n")[0].title()
            time = value.split("\n")[1]
        
            if station_codes.get(station):
                station_code = station_codes[station]
                routes_list[column] = [station_code]
                if station_code not in list_station_code:
                    list_station_code.append(station_code)
            else:
                if station not in keys_with_problem:
                    keys_with_problem.append(station)


            # print(station + " " +time)
    # Destination loop
    for col in timetable_monday_fw.iter_cols(1, timetable_monday_fw.max_column):
        value = col[3].value
        column = col[3].column 
        if value == None:
            continue

        if len(value.split("\n")) >= 2:
            station = value.split("\n")[0].title()
            time = value.split("\n")[1]
        
            if station_codes.get(station):
                station_code = station_codes[station]
                if routes_list.get(column):
                    routes_list[column].append(station_code)
                if station_code not in list_station_code:
                    list_station_code.append(station_code)
            else:
                if station not in keys_with_problem:
                    keys_with_problem.append(station)

    print(list_station_code)
    print(keys_with_problem)
    return routes_list

def old_match_routes():
    all_routes = routes.get_routes()
    timetable_routes = main()
    timetable_count = 0
    for route in all_routes.values():
        # print(route)
        if len(route["path"]) >= 2:
            route_start = route["path"][0]
            route_end = route["path"][-1]
            count = 0
            for col, stations in timetable_routes.items():
                if len(stations) >= 2 and stations[0] == route_start and stations[1] == route_end:
                    # print(f"Match found: Route {route} matches timetable column {col}")
                    count += 1
            
    
    for route in timetable_routes.values():
        if len(route) >= 2:
            route_start = route[0]
            route_end = route[1]
            if route_start == "EUS" and route_end == "BHM":
                timetable_count += 1    
            count = 0
            routes_matched = []
            for r in all_routes.values():
                if len(r["path"]) >= 2 and r["path"][0] == route_start and r["path"][-1] == route_end:
                    # print(f"Match found: Timetable route {route} matches dataset route {r['path']}")
                    count += 1
                    routes_matched.append(r["count"])
            # if count > 2:
            #     print(routes_matched)
            #     print(f"Timetable route from {route_start} to {route_end} matches {count} dataset routes.")

if __name__ == "__main__":
    main()