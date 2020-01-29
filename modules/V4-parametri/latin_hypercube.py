import numpy as np
from model import *
from robustness_eval import run_model_and_get_value
import pickle
import pyDOE

sample_methods = [None,"center","maxmin","centermaximin","correlation"]

# def lhssample(n,p):
#     x= np.random.uniform(size=[n,p])
#     for i in range(p):
#         x[:,i] = (np.argsort(x[:,i])+0.5)/n
#     return x

#stavicemo da mozemo da biramo izmedju raznih lhssample techniques. Tj. odradicu ih za sve.
    # “center” or “c”: center the points within the sampling intervals
    # “maximin” or “m”: maximize the minimum distance between points, but place the point in a randomized location within its interval
    # “centermaximin” or “cm”: same as “maximin”, but centered within the intervals
    # “correlation” or “corr”: minimize the maximum correlation coefficient

#print(x)
# assert(False)
# x = lhssample(samples,num_of_params)

#za svaki sample cemo imati
# prvo, koje cemo parametre imati



#broj stepena otrovnosti
#broj hrane po kvadratnom metru [0,0.1...100], da fiksiramo da bude 100*100 tabla
#ajde prvo da bude isto kao tamo
# agent_memory_size = 
# walk energy
# num agents???? ako bude vise hrane vise ce ih pojesti, mislim da svi treba da idu u istu grupu
# walk energy


def generate_parameter_dict(param_values,velicina):
    # def clamp(n, minn, maxn):
    #     return max(min(maxn, n), minn)
    # def round_up_to_even_and_clamp(f,minn,maxn):
    #     import math
    #     print (minn,maxn)
    #     cl = clamp(f,minn,maxn)
    #     return math.floor(cl / 2.) * 2
    parameter_names=["N","size",
                     "br_hrane_po_stepenu","br_stepena_otrovnosti",
                     "agent_memory_size","agent_walk_energy"]
    parameter_scale = [1,1,
                       0.1,1,
                       1,0.01]
    parameter_scale = [s*velicina for s in parameter_scale]
    food_num = param_values[2]*velicina
    converters = [int,int,
                  int,lambda x: 10,
                  #                  lambda x: round_up_to_even_and_clamp(x,2,food_num/2),
                  int,float]
    
    parameters = {k:c(v*s) for (k,v,s,c) in zip(parameter_names,param_values,parameter_scale,converters)}
    return parameters

all_results=[]
OUTPUT_PARAMETER="AverageEnergyPerCapita"

def run_for_param_set(param_values):
    # velicine = [str(v)[::-1].find(".") for v in param_values]
    # assert(velicine.count(velicine[0]) == len(velicine))
    # velicina = 10**velicine[0]
    #    assert(velicina<=1000)
    SAMPLE_SIZE = 100
    velicina = 1000 #ove mozemo menjati da vidimo kako se ponasa sa drugim, samo to mora da ide sa sample sizom. ako ima
    #50 ss, onda ce svejedno vec pola uzeti
    parameters=generate_parameter_dict(param_values,velicina)
    print (parameters)
    results_for_same=[]
    for i in range(SAMPLE_SIZE):
        print(i)
        res=run_model_and_get_value(parameters,output_parameter=OUTPUT_PARAMETER,num_of_steps=500)
        results_for_same.append(res)
    print (results_for_same)
    parameters[OUTPUT_PARAMETER+"_median"]=np.median(results_for_same)
    return parameters

import multiprocessing
import time
num_of_params = 6
for c in sample_methods:
    x = pyDOE.lhs(n=6,samples =50,criterion = c)
    pool = multiprocessing.Pool(2)
    all_results = pool.map(run_for_param_set,x)
    with open("lhc-{}-{}.pkl".format(c,time.asctime()),"wb") as f:
        pickle.dump(all_results,f,pickle.HIGHEST_PROTOCOL)
    df = pd.DataFrame(all_results)
    df.to_csv("lhc-{}-{}.csv".format(c,time.asctime()))
    print (all_results)
# all_results = []
# for param_values in x:
#     parameters = run_for_param_set(param_values)
#     all_results.append(parameters)


        

#ok ovo funkionise, imamo nase parametre, i sad mozemo da ih prosledimo
    
