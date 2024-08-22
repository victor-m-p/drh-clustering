import numpy as np
import pandas as pd

# provide example of cluster #
EM_q = pd.read_csv("../data/EM/EM_q_group.csv")
EM_theta = pd.read_csv("../data/EM/EM_theta_group.csv")
EM_theta[["question_short", "dim0"]].round(4)

# find entries for example #
answers = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")

# muscular christianity
muscular_christianity = answers[answers["entry_id"] == 771]

"""
0 for ritual observance
1 for conversion of non-religionists
1 for anthropomorphic
1 for unquestionably good 
0 for permissible to worship other god
1 for taboos 
"""

free_methodist = answers[answers["entry_id"] == 879]
free_methodist

""" 
0 for ritual observance
1 for conversion of non-religionists
0 for anthropomorphic
1 for unquestionably good
0 for permissible to worship other god
0 for taboos
"""
