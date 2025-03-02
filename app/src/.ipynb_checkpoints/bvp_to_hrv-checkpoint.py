import pickle
import pyhrv.time_domain as td
import time

start_time = time.perf_counter()

with open('../data/nni.pkl', 'rb') as file:
    nni_seq = pickle.load(file)

results = td.time_domain(nni=nni_seq)
print(results)
results['nni_histogram'].savefig('../data/nni_histogram.png')
results = results.__dict__
results.pop('nni_histogram', None)

with open('../data/hrv_result.pkl', 'wb') as f:
    pickle.dump(results, f)
    
end_time = time.perf_counter()
print(f"Execution time: {end_time - start_time} seconds")