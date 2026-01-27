import pyarrow.parquet as pq
import json
from datetime import datetime 

trip_parquet_file_path = ".output/timetable/trips.parquet"
unique_timestamps_file_path = ".output/timetable/timelist.parquet"

def main():
    trips_analysis()
    timestamps_analysis()

def timestamps_analysis():
    timestamps = pq.read_table(unique_timestamps_file_path)
    for timestamp in timestamps:
        print(timestamp)

def trips_analysis():
    trips = pq.read_table(trip_parquet_file_path).to_pylist()
    print(len(trips))
    unique_start_station = []
    unique_final_station = []
    for trip in trips:
        start_station = trip["path"][0]
        final_station = trip["path"][-1]
        if start_station not in unique_start_station:
            unique_start_station.append(start_station)
        if final_station not in unique_final_station:
            unique_final_station.append(final_station)
    print("Number of unique start stations:" + str(len(unique_start_station)))
    print(unique_start_station)
    print("Number of unique final stations:" + str(len(unique_final_station)))
    print(unique_final_station)

    

if __name__ == "__main__":
    main()