import pyarrow.parquet as pq
import json
from datetime import datetime 

trip_parquet_file_path = ".output/timetable/trips.parquet"
unique_timestamps_file_path = ".output/timetable/timelist.parquet"

def main():
    trips = pq.read_table(trip_parquet_file_path).to_pylist()
    trips_analysis(trips)
    timestamps_analysis()
    distribution(trips)

def timestamps_analysis():
    timestamps = pq.read_table(unique_timestamps_file_path)
    for timestamp in timestamps:
        pass
        # print(timestamp)
## Visualization for the time distribution and station pair distribution

# Check the distribution between pairs of trips
def distribution(trips):
    distribution = {}
    for trip in trips:
        start_station = trip["path"][0]
        final_station = trip["path"][-1]
        pair = start_station + "-" + final_station
        if distribution.get(pair):
            distribution[pair] +=1
        else:
            distribution[pair] = 1
    print(distribution)

def trips_analysis(trips):
    print(len(trips))
    unique_start_station = []
    unique_final_station = []
    unique_station = []
    for trip in trips:
        start_station = trip["path"][0]
        final_station = trip["path"][-1]
        for station in trip["path"]:
            if station not in unique_station:
                unique_station.append(station)
        if start_station not in unique_start_station:
            unique_start_station.append(start_station)
        if final_station not in unique_final_station:
            unique_final_station.append(final_station)
    print("Number of unique start stations:" + str(len(unique_start_station)))
    print(unique_start_station)
    print("Number of unique final stations:" + str(len(unique_final_station)))
    print(unique_final_station)
    print("Number of unique stations:" + str(len(unique_station)))
    print(unique_station)

    

if __name__ == "__main__":
    main()