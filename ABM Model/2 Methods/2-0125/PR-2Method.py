import csv
import numpy as np

# Input Method Complexity and Accuracy
methods = {
    'A': {'compx': 8, 'accy': 0.75},
    'B': {'compx': 16, 'accy': 0.95}
}

# Initializing variables
real_value = 100
time_scale = np.arange(10, 401, 10)  # Change to record every 10 units of time

# Function to calculate probability
def calc_prob(method, time, real_value):
    accy = methods[method]['accy']
    compx = methods[method]['compx']
    prob = (1 - abs(real_value - (real_value * accy)) / real_value)
    return prob if time >= compx else prob / (compx - time)

# Function to calculate Bayesian updates
def bayesian_update(PmA, PmB):
    total = PmA + PmB
    ExeA, ExeB = PmA / total, PmB / total
    BayA = (PmA * ExeA) / ExeB
    BayB = (PmB * ExeB) / ExeA
    return BayA, BayB

# Start and record simulations
output = []
for round_index, time in enumerate(time_scale):
    PmA = calc_prob('A', round_index, real_value)
    PmB = calc_prob('B', round_index, real_value)
    
    BayA, BayB = bayesian_update(PmA, PmB)
    total_bay = BayA + BayB
    RtBA, RtBB = BayA / total_bay, BayB / total_bay
    
    output.append({
        "Time": time,
        "Complex A": methods['A']['compx'],
        "Complex B": methods['B']['compx'],
        "Ratio A": PmA,
        "Ratio B": PmB,
        "Exe A": PmA / (PmA + PmB),
        "Exe B": PmB / (PmA + PmB),
        "PR A": RtBA,
        "PR B": RtBB
    })

# Write main output to CSV
output_fn = 'PR-2Method.csv'
with open(output_fn, 'w', newline='') as fout:
    writer = csv.DictWriter(fout, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)

# Function to create a CSV with the highest PR method at given intervals
def create_highest_pr_csv(start, interval, filename):
    highest_pr_output = []
    for time in range(start, 401, interval):
        for entry in output:
            if entry["Time"] == time:
                pr_values = {'A': entry['PR A'], 'B': entry['PR B']}
                highest_pr_method = max(pr_values, key=pr_values.get)
                highest_pr_output.append({
                    "Time": entry["Time"],
                    "Choice": highest_pr_method
                })
                break

    with open(filename, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=["Time", "Choice"])
        writer.writeheader()
        writer.writerows(highest_pr_output)

# Create the additional CSV files
create_highest_pr_csv(20, 20, 'Highest_PR_Method_20-2P.csv')
create_highest_pr_csv(50, 50, 'Highest_PR_Method_50-2P.csv')
create_highest_pr_csv(80, 80, 'Highest_PR_Method_80-2P.csv')
