#!/usr/bin/env python
# script to take all the absent organisms and calculate the ANI of them to the reference database
import os
os.chdir('./experiments/mut_thresh_spike')
import sourmash
import multiprocessing
from itertools import repeat
import numpy as np
import matplotlib.pyplot as plt

reference_name = "prefetch_formatted_db_to_gtdb.sig"
EU_training_name = "formatted_db.sig"
# import the reference database
reference_db = sourmash.load_file_as_signatures(reference_name)
ref_sigs = {sketch.name.split('.')[0]: sketch for sketch in reference_db}
# import the absent organisms
EU_training_db = sourmash.load_file_as_signatures(EU_training_name)
EU_training_sigs = {sketch.name.split('.')[0]: sketch for sketch in EU_training_db}

def map_func(ref_sig, EU_training_sketches):
    # map function to calculate the ANI of the absent organisms to the reference database
    max_ani = 0
    max_name = None
    for absent_name, absent_sketch in EU_training_sketches.items():
        ani = absent_sketch.max_containment_ani(ref_sig, estimate_ci=True).ani_high
        if ani > max_ani:
            max_ani = ani
            max_name = absent_name
    return ref_sig.name, max_ani, max_name


def map_star(args):
    # wrapper function to unpack the arguments
    return map_func(*args)

# now we can calculate the ANI of the absent organisms to the reference database in parallel
pool = multiprocessing.Pool(processes=16)
results = pool.map(map_star, zip(ref_sigs.values(), repeat(EU_training_sigs)))
pool.close()
pool.join()
# now we can write the results to a file
with open('absent_ani.csv', 'w') as f:
    f.write('reference,max_ani,max_ani_name')
    for ref_name, ani, name in results:
        f.write(f'{ref_name},{ani},{name}')

values = np.array([x[1] for x in results])
# select those about 0.7
big_vals = values[values > 0.7]

# plot a histogram of the ANIs
plt.figure()
plt.hist(values, bins=100)
plt.show()


# Remaining to do:
# Subselect the prefetch_formatted_db_to_gtdb.sig to only include those that are not in the actual sample
# Then run the above script to get the ANI of the absent organisms to the reference database
