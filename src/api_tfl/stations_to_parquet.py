import requests
import lines as l
import pyarrow as pa
import pyarrow.parquet as pq
import os

def get_all_stations(lines):
    stations = {}
    for line in lines: 
        result = get_stations_per_line(line=line["name"])
        if len(result) == 0:
            continue
        create_station(stations,result)
    print(stations)
    return stations

def get_stations_per_line(line:str):
    inbound = requests.get("https://api.tfl.gov.uk/Line/"+ line + "/StopPoints")
    return inbound.json()

def create_station(stations, r_inbound):
    for station in r_inbound:
        if stations.get(station["stationNaptan"]):
            continue
        station_dict = {}
        id_station = station["stationNaptan"]
        station_dict["id"] = id_station
        station_dict["lat"] = station["lat"]
        station_dict["lon"] = station["lon"]
        station_dict["name"] = station["commonName"]
        stations[station["stationNaptan"]] = station_dict

def save_station_parquet(stations):
    schema = pa.schema([
        ('id',pa.string()),
        ('lat', pa.float64()),          
        ('lon', pa.float64()), 
        ('name', pa.string())
    ])
    stationsTable = pa.Table.from_pylist(stations,schema)
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")
    if not os.path.exists(os.path.join(os.getcwd(), '.output/timetable_tfl')):
        os.mkdir(".output/timetable_tfl", mode=0o777, dir_fd=None)
    pq.write_table(stationsTable,".output/timetable_tfl/stations.parquet")

def main():
    # Get all lines for TFL (Using a hardcoded file)
    lines = l.get_lines()
    # # Extract all stations using the london tfl api 
    stations = get_all_stations(lines)
    save_station_parquet(stations=stations.values())

main()