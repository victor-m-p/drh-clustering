import pandas as pd
import numpy as np


# check whether we have entries that are both islamic and christian
def convert_logodds(x):
    return 100 * np.exp(x) / (1 + np.exp(x))


# extract logodds from monitoring data
monitoring_population = pd.read_csv("../data/mdl/monitoring_conversion_population.csv")
intercept_logodds = monitoring_population[
    monitoring_population["Hypothesis"] == "(Intercept) > 0"
]["Estimate"].values[0]
year_logodds = monitoring_population[
    monitoring_population["Hypothesis"] == "(year_norm) > 0"
]["Estimate"].values[0]
christian_logodds = monitoring_population[
    monitoring_population["Hypothesis"] == "(christian) > 0"
]["Estimate"].values[0]

# convert logodds to probabilities
intercept_natural = convert_logodds(intercept_logodds)
late_entry = convert_logodds(intercept_logodds + year_logodds)
christian = convert_logodds(intercept_logodds + year_logodds + christian_logodds)

# check earliest and latest year from
monitoring = pd.read_csv("monitoring_conversion.csv")
monitoring["year_from"].min()  # -3500
monitoring["year_from"].max()  # 2022
