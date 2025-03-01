import pickle
import pyhrv.time_domain as td

with open('nni.pkl', 'rb') as file:
    nni_seq = pickle.load(file)

results = td.time_domain(nni=nni_seq)
print(results)