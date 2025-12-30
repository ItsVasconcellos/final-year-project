import openpyxl
import network
import routes

def main():
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

def match_routes():
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
    print(f"Total timetable routes matching EUS to BHM: {timetable_count}")

match_routes()