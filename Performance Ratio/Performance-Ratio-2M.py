#Generate Model Sampling 

import random, csv
import pandas as pd
import numpy as np

#total timeframe equals 400
#max complexity 15

#Input Method Complexity
Method_A_compx = 3
Method_B_compx = 5

#Input how each Method is close to reality (between 0 and 1)
Method_A_accy = 0.50
Method_B_accy = 0.60


#Start and record simulations
o = list()
Real_Value=100
Rounds = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#Each round represent a given time scale
Time_Scale = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]

for time in Rounds:
    if int(f"{time}") >=Method_A_compx:
        PmA = (1 - (abs(Real_Value-(Real_Value*Method_A_accy))/Real_Value))
    else: 
        PmA = (1 - (abs(Real_Value-(Real_Value*Method_A_accy))/Real_Value)) / (Method_A_compx-int(f"{time}"))
        
    if int(f"{time}") >=Method_B_compx:
        PmB = (1 - (abs(Real_Value-(Real_Value*Method_B_accy))/Real_Value))
    else: 
        PmB = (1 - (abs(Real_Value-(Real_Value*Method_B_accy))/Real_Value)) / (Method_B_compx-int(f"{time}"))
        
    
    #Start Bayesian Update
    ExeA = PmA / (PmA+PmB)
    ExeB = PmB / (PmA+PmB)

    BayA = (PmA*ExeA)/(ExeB)
    BayB = (PmB*ExeB)/(ExeA)

    #Calculate Real Time Performance Ratio
    RtBA = BayA / (BayA+BayB)
    RtBB = BayB / (BayA+BayB)
    
    nl = dict()
        
    nl[f"Time"]=f"{time}"
    nl[f"Complex A"]=f"{Method_A_compx}"
    nl[f"Complex B"]=f"{Method_B_compx}"
    nl[f"Ratio A"]=f"{PmA}"
    nl[f"Ratio B"]=f"{PmB}"
    nl[f"Exe A"]=f"{ExeA}"
    nl[f"Exe B"]=f"{ExeB}"
    nl[f"PR A"]=f"{RtBA}"
    nl[f"PR B"]=f"{RtBB}"
            
    o.append(nl)
        
output_fn = 'PR-2Method.csv'
with open(output_fn,'w',newline='') as fout:
    writer = csv.DictWriter(fout, fieldnames=o[0].keys())
    writer.writeheader()
    for new_row in o:
        writer.writerow(new_row)
