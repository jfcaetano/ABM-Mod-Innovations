import csv
import numpy as np

# Input Method Complexity and Accuracy
methods = {
    'A': {'compx': 4, 'accy': 0.30},
    'B': {'compx': 9, 'accy': 0.65},
    'C': {'compx': 30, 'accy': 0.90}
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
def bayesian_update(PmA, PmB, PmC):
    total = PmA + PmB + PmC
    ExeA, ExeB, ExeC = PmA / total, PmB / total, PmC / total
    BayA = (PmA * ExeA) / (ExeB + ExeC)
    BayB = (PmB * ExeB) / (ExeA + ExeC)
    BayC = (PmC * ExeC) / (ExeB + ExeA)
    return BayA, BayB, BayC

# Start and record simulations
output = []
for round_index, time in enumerate(time_scale):
    PmA = calc_prob('A', round_index, real_value)
    PmB = calc_prob('B', round_index, real_value)
    PmC = calc_prob('C', round_index, real_value)
    
    BayA, BayB, BayC = bayesian_update(PmA, PmB, PmC)
    total_bay = BayA + BayB + BayC
    RtBA, RtBB, RtBC = BayA / total_bay, BayB / total_bay, BayC / total_bay
    
    output.append({
        "Time": time,
        "Complex A": methods['A']['compx'],
        "Complex B": methods['B']['compx'],
        "Complex C": methods['C']['compx'],
        "Ratio A": PmA,
        "Ratio B": PmB,
        "Ratio C": PmC,
        "Exe A": PmA / (PmA + PmB + PmC),
        "Exe B": PmB / (PmA + PmB + PmC),
        "Exe C": PmC / (PmA + PmB + PmC),
        "PR A": RtBA,
        "PR B": RtBB,
        "PR C": RtBC
    })

# Write main output to CSV
output_fn = 'PR-3Method.csv'
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
                pr_values = {'A': entry['PR A'], 'B': entry['PR B'], 'C': entry['PR C']}
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
create_highest_pr_csv(20, 20, 'Highest_PR_Method_20-3P.csv')
create_highest_pr_csv(50, 50, 'Highest_PR_Method_50-3P.csv')
create_highest_pr_csv(80, 80, 'Highest_PR_Method_80-3P.csv')
