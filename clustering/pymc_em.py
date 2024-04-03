'''
vmp 5-8-23;
experimental using dimensions as predictors. 
nothing significant--but all dimensions trending positive.
what does this mean? 
'''

import matplotlib.lines as mlines
from itertools import product
import seaborn as sns 
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd 
import os 
from fun import remove_duplicates
import pymc as pm
import arviz as az 
RANDOM_SEED=413
rng = np.random.default_rng(RANDOM_SEED)

# dimensions from em_pipeline.py
superquestion = 'shg'
data = pd.read_csv(f'fig/{superquestion}_dim0_entries.csv')

# entry metadata
entry_metadata=pd.read_csv('../data/preprocessed/entry_metadata.csv')
entry_metadata['log_sq_km']=np.log(entry_metadata['region_area'])
entry_metadata['start_year_norm']=entry_metadata['start_year'] / entry_metadata['start_year'].max()
entry_metadata = entry_metadata[['entry_id', 'start_year_norm', 'log_sq_km']].drop_duplicates()

# final data
superquestions = pd.merge(data, entry_metadata, on='entry_id', how='inner')
superquestions = superquestions.sort_values('entry_id')

### model ###
with pm.Model() as model_interact:
    # hyperpriors
    sigma=pm.HalfNormal('sigma', sigma=5)
    
    # priors
    intercept = pm.Normal('intercept', mu=0, sigma=5)
    time = pm.Normal('time', mu=0, sigma=5)
    dim0 = pm.Normal('dim0', mu=0, sigma=5)
    dim1 = pm.Normal('dim1', mu=0, sigma=5)
    dim2 = pm.Normal('dim2', mu=0, sigma=5)
    
    # linear model
    mu = intercept + time * superquestions['start_year_norm'] + dim0 * superquestions['dim0'] + dim1 * superquestions['dim1'] + dim2 * superquestions['dim2']
    
    # likelihood
    y = pm.Normal('y', mu=mu, sigma=sigma, observed=superquestions['log_sq_km'])
    
    # trace
    trace = pm.sample(2000, 
                      tune=2000, 
                      target_accept=0.9,
                      random_seed=rng,
                      )
    pm.sample_posterior_predictive(trace,
                                   extend_inferencedata=True,
                                   random_seed=rng)

### check fit ###
# samples look good
fig, ax = plt.subplots()
az.plot_trace(trace)
plt.tight_layout()
plt.show();

# looks bad but not terrible
az.plot_ppc(trace)
az.plot_ppc(trace, kind='cumulative')

# nothing significant--all trending though (have not looked at these)
# why are they all positive in both cases; is there something weird here?
# just an effect of "having more" gives more "area"?
az.summary(trace)