"""
VMP 2024-09-21 write latex tables of outputs
"""

import pandas as pd

monitoring_pop = pd.read_csv("../data/mdl/monitoring_conversion_population.csv")
monitoring_pop.to_latex(
    "../tables/monitoring_conversion_population.tex", index=False, float_format="%.2f"
)

monitoring_grp = pd.read_csv("../data/mdl/monitoring_conversion_group.csv")
monitoring_grp.to_latex(
    "../tables/monitoring_conversion_group.tex", index=False, float_format="%.2f"
)

shg_pop = pd.read_csv("../data/mdl/shg_unquestionably_population.csv")
shg_pop.to_latex(
    "../tables/shg_conversion_population.tex", index=False, float_format="%.2f"
)

shg_group = pd.read_csv("../data/mdl/shg_unquestionably_group.csv")
shg_group.to_latex(
    "../tables/shg_conversion_group.tex", index=False, float_format="%.2f"
)
