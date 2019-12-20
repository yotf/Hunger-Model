
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
ConsistencyTuple = namedtuple("ConsistencyResult","br_koraka sample_size maxA")
#ok krecemo
brojevi_koraka = [50,100,250,500,1000]
brojevi_koraka = [50,100,250,500]

sample_sizes = [1,5,50,100,300]
lista_rezultata = []
parameter_res_dict = defaultdict(list)
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
MAX_STEPS = 500
sample_size_to_max_A = dict()

def get_model_results(number):
    """Vraca rezultata date velicine size"""
    results =[]
    for i in range(number):    
        model = HungerModel(NUM_AGENTS,WIDTH,HEIGHT)
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
    print ("MAX A measure for sample size %s" %ss)
    print (max(A_measures))
    return max(A_measures)
    
    

for ss in sample_sizes:
    all_results_for_samplesize = []
    for i in range(20):
        results = get_model_results(ss)
        #sad imamo toliko koliko imamo samplova, toliko imamo rezultata, sad bi bilo
        #dobro da uradimo sledece, da napravimo
        all_results_for_samplesize.append(results)

    parameters=["TotalEnergy"]
    
    for parameter in parameters:
        for steps in brojevi_koraka:
            maxA = get_maxA_for_steps_and_parameter(all_results_for_samplesize,steps,parameter)
            parameter_res_dict[parameter].append(ConsistencyTuple(steps,ss,maxA))

    print (parameter_res_dict)
    import pandas as pd
    import matplotlib.pyplot as plt
    
    for key,results in parameter_res_dict.items():
        df = pd.DataFrame(results,columns = ["br_koraka","sample_size","maxA"])
        df.pivot("sample_size","br_koraka","maxA").plot(kind="bar")
        plt.show()
                          
        

#    konstuple = ConsistencyTuple(br_koraka=br_koraka,sample_size=ss,value=rez)

