#Prvo imamo parametre koje prosledjujemo glavnom procsesu
# Znaci ono sto radimo en gros je, prikupljamo 20 samplova od po (1,5,50,100,300) uzoraka
# To ce biti prvo, i onda cemo ih porediti sve, sto se tice A measure
# Rezultati ce biti {1:A-mes,5:A-mes (between twenty)}, itd i mozemo ih predstaviti kao
#barplot, to moze biti posle interaktivno u simulaciji napravljeno kako bismo mogli da vidimo zavisnost
#od runova. Ali to kasnije. Za sada je vazno da vidimo kolika je konzistentnost izmedju rezultata Zapisuje
# 1000 koraka npr (posle cemo zabeleziti i sve ostale, ustvari mozemo napraviti bar plotove, bice
#grupisani po sample size (1,5...), i u jednoj grupi ce biti rezultati za 50,100,250,500,100), i onda cemo
#moci sve da ih poredimo
# Za sada cemo da se fokusiramo na energiju ukupnu npr.


#sintaksa za grouped barplot je  [['100','1',x],...['1000','300',z]] [br_koraka,br_grupe,A-vr]

#ovo ce biti grafici, a posle cemo naci onaj najmanji koji zadovoljava, za svaki parametar, i to mozemo
#napraviti kao grafik
from collections import namedtuple,defaultdict
from model import *
import seaborn as sns
sns.set()
ConsistencyTuple = namedtuple("ConsistencyResult","br_koraka sample_size maxA")
#ok krecemo
brojevi_koraka = [50,100,250,500,1000]
#brojevi_koraka = [50,100,250,500]

sample_sizes = [1,5,50,100,300]
#sample_sizes = [1,5,50]
lista_rezultata = []
#A measure se meri tako sto se prva grupa poredi sa drugom, znaci, ako imamo 20 distribucije
#od po 5 samplova. Svaki iz prve grupe poredimo sa svakim iz ostalih grupa


def A_measure(dist1,dist2):
    greater_than = 0
    equal = 0
    for sample1 in dist1:
        for sample2 in dist2:
            if sample1>sample2:
                greater_than+=1
            if sample1==sample2:
                equal+=1
    ld1 = len(dist1)
    ld2 = len(dist2)
    ld12 = ld1*ld2
    return greater_than/ld12 + 0.5*(equal/ld12)

def A_measure2(dist1,dist2):
    import itertools
    sve_kombinacije = list(itertools.product(dist1,dist2))
    greater_than = sum([s1>s2 for (s1,s2) in sve_kombinacije])
    equal = sum([s1==s2 for (s1,s2) in sve_kombinacije])
    mn = len(dist1)*len(dist2)
    return greater_than/mn + 0.5*(equal/mn)


VALUE = "TotalEnergy"      
NUM_AGENTS = 20
WIDTH = 10
HEIGHT = 10
DIMENZIJA_TABLE=10
MAX_STEPS = 500
sample_size_to_max_A = dict()

def get_model_results(number):
    """Vraca rezultata date velicine size"""
    results =[]
    for i in range(number):    
        model = HungerModel(**generate_parameter_dict_fixed())
        for i in range(MAX_STEPS):
            model.step()
        rez =model.datacollector.get_model_vars_dataframe()
        results.append(rez)
#        distribution.append(rez.iloc[-1][VALUE])
    return results


def compare_first_with_others(distributions):
    A_measures=[]
    first = distributions[0]
    for other in distributions[1:]:
        A = A_measure2(first,other)
        A_measures.append(A)
    return A_measures

def A_measure_every_with_every(distributions):
    A_measures = []
    for d1 in distributions:
        for d2 in [d for d in distributions if d is not d1]:
            assert(d2!=d1)
            assert(d2 is not d1)
            A= A_measure2(d1,d2)
            A_measures.append(A)
    print (len(A_measures))
    return A_measures

def get_maxA_for_steps_and_parameter(all_results_for_samplesize,steps,parameter):
    distributions = []
    for results in all_results_for_samplesize:
        distribution = []
        for result in results:
            value = result[:steps].iloc[-1][parameter]
            distribution.append(value)
        distributions.append(distribution)
    
    A_measures = compare_first_with_others(distributions)
    print (A_measures)
    assert(len(A_measures)==19)
    print (max(A_measures))
    return max(A_measures)

def check_consistency_parallel(PARAMETER = "AverageEnergyPerCapita"):
    pass
#    def get_results_for_sample_size():
    #za svaki sample size pravimo dvadeset i racunamo a measure. Mozemo da parelilizujemo
    #trazenje tih dvadeste



    

def check_conistency(PARAMETER="AverageEnergyPerCapita"):
    import pandas as pd
    import matplotlib.pyplot as plt
    results_list = []
    for ss in sample_sizes:
        all_results_for_samplesize = []
        for i in range(20):
            results = get_model_results(ss)
            all_results_for_samplesize.append(results)
        for steps in brojevi_koraka:
            maxA = get_maxA_for_steps_and_parameter(all_results_for_samplesize,steps,PARAMETER)
            results_list.append(ConsistencyTuple(steps,ss,maxA))
            print (results_list)

    df = pd.DataFrame(results_list,columns = ["br_koraka","sample_size","maxA"])
    df.to_csv("check_consistency-0.csv")
    df.pivot("sample_size","br_koraka","maxA").plot(kind="bar")
    plt.show()


def generate_parameter_dict_fixed():
    NUM_AGENTS = 10
    DIMENZIJA_TABLE = 10

    STEPENI_OTROVNOSTI =4
    KOLICINA_ZA_SVAKU_OTROVNOST = 15
    BROJ_HRANE = STEPENI_OTROVNOSTI*KOLICINA_ZA_SVAKU_OTROVNOST
    MEMORIJA_AGENATA = 24
    WALK_ENERGY =0.2
    #prvo ajd probamo memoriju
    parameters = {"N":NUM_AGENTS,
                  "size":DIMENZIJA_TABLE,
                 "br_hrane_po_stepenu":KOLICINA_ZA_SVAKU_OTROVNOST,
                 "br_stepena_otrovnosti":STEPENI_OTROVNOSTI,
                 "agent_memory_size":MEMORIJA_AGENATA,
                 "agent_walk_energy":WALK_ENERGY
                 }
    return parameters



def run_model_and_get_value(parameters,output_parameter,num_of_steps):
    model = HungerModel(**parameters)
    for i in range(num_of_steps):
        model.step()
    rez =model.datacollector.get_model_vars_dataframe()
    return rez.iloc[-1][output_parameter]

def run_range(i,INPUT_PARAMETER,OUTPUT_PARAMETER,parameters):
    num_of_samples = 100
    parameters[INPUT_PARAMETER] = i
    distribution = []
    print ("INPUT PARAMETER : %s INPUT VALUE :%s" %(INPUT_PARAMETER,i))
    for i in range(num_of_samples):
        rez = run_model_and_get_value(parameters,OUTPUT_PARAMETER,num_of_steps = 500)
        distribution.append(rez)
    assert(len(distribution)==num_of_samples)
    return distribution

def robustness_eval(INPUT_PARAMETER,range_of_input,OUTPUT_PARAMETER):

    import multiprocessing
    from itertools import repeat
    range_of_input = list(range_of_input)
    parameters = generate_parameter_dict_fixed()
    pool = multiprocessing.Pool(3)
    distributions = pool.starmap(run_range,zip(range_of_input,repeat(INPUT_PARAMETER),repeat(OUTPUT_PARAMETER),repeat(parameters)))
    # for i in range_of_input:
    #     print ("INPUT PARAMETER : %s INPUT VALUE :%s" %(INPUT_PARAMETER,i))
    #     parameters[INPUT_PARAMETER]= i
    #     distribution=[]
    #     pool = multiprocessing.Pool(4)
    #     distribution = pool.starmap(run_model_and_get_value,zip([parameters]*num_of_samples,[OUTPUT_PARAMETER]*num_of_samples,[500]*num_of_samples))
    #     # for i in range(num_of_samples):
    #     #     rez = run_model_and_get_value(parameters,OUTPUT_PARAMETER,num_of_steps = 500)
    #     #     distribution.append(rez)
    #     assert(len(distribution)==num_of_samples)
    #     distributions.append(distribution)
    print ("LEN OF DISTRIBUTIONS")
    print (len(distributions))
    A_measures = A_measure_every_with_every(distributions)

    print (A_measures)
    print (max(A_measures))
    return A_measures


def prepare_and_run_robustness_eval():
    from numpy import arange
    import pickle
    import pandas as pd
    import time
    params = generate_parameter_dict_fixed().keys()

    input_to_range = {"N":range(2,51,2),
                 "size":range(2,51,2),
                 "br_hrane_po_stepenu":range(2,51,2),
                 "br_stepena_otrovnosti":range(2,51,2),
                "agent_memory_size":range(2,51,2),
                 "agent_walk_energy":arange(0.1,2.6,0.1)
                 }
    length = len(list(input_to_range["N"]))
    assert(all(len(list(rng))==length for rng in input_to_range.values()))
    params_As = {}
    for param in params:
        INPUT_PARAMETER = param
        A_measures =robustness_eval(OUTPUT_PARAMETER="AverageEnergyPerCapita",range_of_input=input_to_range[INPUT_PARAMETER],INPUT_PARAMETER=INPUT_PARAMETER)
        params_As[param]=A_measures


    with open("dict_robustness-{}.pkl".format(time.asctime()),"wb") as f:
        pickle.dump(params_As,f,pickle.HIGHEST_PROTOCOL)
    df = pd.DataFrame(params_As)
    print (params_As)
    print(df)
    df.to_csv("robustness_svaki_sa_svakim-{}.csv".format(time.asctime()))
    

if __name__=="__main__":
#    check_conistency()
    prepare_and_run_robustness_eval()

#    konstuple = ConsistencyTuple(br_koraka=br_koraka,sample_size=ss,value=rez)

