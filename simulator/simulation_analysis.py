import main as simulation
import json
import os

# Config
types = ["degree", "betweeness", "closeness"]
percentages = [2, 4, 6, 8, 10] 
max_delays = [1, 3, 6, 9, 12, 15]
runs_per_config = 10
sim_type = "degree"
output_file = ".output/simulation/simulation_results.jsonl"

def sum_dict_values(d1, d2):
    """Adds values of two dictionaries together by key."""
    result = d1.copy()
    for key, value in d2.items():
        result[key] = result.get(key, 0) + value
    return result

def save_to_jsonl(data, filename):
    """Appends a single flat object to the JSONL file."""
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")

def main():
    # Remove old file if starting fresh
    if not os.path.exists(os.path.join(os.getcwd(), '.output')):
        os.mkdir(".output")
    if not os.path.exists(os.path.join(os.getcwd(), '.output/simulation')):
        os.mkdir(".output/simulation", mode=0o777, dir_fd=None)
    else:
        os.remove(output_file)
    for t in types:
        sim_type = t
        for p in percentages:
            for delay in max_delays:
                # 1. Initialize accumulators
                avg_t_delay_gen = 0
                avg_t_delay_propagated = 0
                avg_t_trips_delayed = 0
                total_dist_trips_delayed = {}
                total_dist_stations_delayed = {}

                print(f"Processing: % {p} | Delay {delay} | Type: {sim_type}")

                for i in range(runs_per_config):
                    # Run the simulation
                    d_gen, d_prop, t_trips, dist_trips, dist_stations = simulation.main(
                        d_percentage=p, 
                        d_type=sim_type, 
                        d_minutes=delay
                    )
                    
                    # Accumulate raw values
                    avg_t_delay_gen += d_gen
                    avg_t_delay_propagated += d_prop
                    avg_t_trips_delayed += t_trips
                    total_dist_trips_delayed = sum_dict_values(total_dist_trips_delayed, dist_trips)
                    total_dist_stations_delayed = sum_dict_values(total_dist_stations_delayed, dist_stations)
                # percentage increase of delay in terms of time
                # Mix with the amount of delay per trip and use a heat map(check it)

                # 2. Calculate Averages
                record = {
                    "type": sim_type,
                    "percentage": p,
                    "max_delay": delay,
                    "runs_averaged": runs_per_config,
                    "avg_delay_generated": avg_t_delay_gen / runs_per_config,
                    "avg_delay_propagated": avg_t_delay_propagated / runs_per_config,
                    "avg_trips_delayed": avg_t_trips_delayed / runs_per_config,
                    "avg_dist_stations": {k: v for k, v in total_dist_stations_delayed.items()},
                    "avg_dist_trips": {k: v for k, v in total_dist_trips_delayed.items()}
                }

                # 3. Save the averaged result immediately
                save_to_jsonl(record, output_file)

if __name__ == "__main__":
    main()